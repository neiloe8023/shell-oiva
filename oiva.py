import sys
import re
import os
import tomli
from openai import OpenAI


def print_usage():
    """打印使用说明"""
    print("用法: python oiva.py <您的问题>")
    print("示例: python oiva.py 怎么打印文件列表")


class ShellOiva:
    def __init__(self, config_path=None):
        """初始化ShellOiva类"""
        # 如果没有指定配置文件路径，则使用与可执行文件相同目录下的config.toml
        if config_path is None:
            # 获取可执行文件所在的目录路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的可执行文件
                executable_dir = os.path.dirname(sys.executable)
            else:
                # 如果是直接运行的Python脚本
                executable_dir = os.path.dirname(os.path.abspath(__file__))
            
            config_path = os.path.join(executable_dir, "config.toml")
            
        # 读取配置文件
        self.config = self._load_config(config_path)
        
        # 从配置中获取API设置
        api_key = self.config["api"]["api_key"]
        base_url = self.config["api"]["base_url"]
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        # 从配置中获取其他设置
        self.clean_output = self.config["output"]["clean_output"]
        self.temperature = self.config["output"]["temperature"]
        self.prompt = self.config["system"]["prompt"]
        self.model = self.config["api"]["model"]
    
    @staticmethod
    def _load_config(config_path):
        """加载TOML配置文件"""
        # 确保配置文件存在
        if not os.path.exists(config_path):
            print(f"错误: 找不到配置文件 '{config_path}'")
            print("请确保配置文件与可执行文件位于同一目录")
            sys.exit(1)
        
        # 读取配置文件
        try:
            with open(config_path, "rb") as f:
                return tomli.load(f)
        except Exception as e:
            print(f"错误: 无法读取配置文件: {e}")
            sys.exit(1)

    @staticmethod
    def clean_response(text):
        """移除回答中的代码包裹符号和语言标识"""
        # 移除开始的 ```language 标记
        text = re.sub(r'^```\w*\n', '', text)
        # 移除结束的 ``` 标记
        text = re.sub(r'\n```$', '', text)
        # 移除单独一行的 ``` 标记
        text = re.sub(r'^```$', '', text, flags=re.MULTILINE)
        return text

    def process_query(self, user_query):
        """处理用户查询并返回结果"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=self.temperature,
            stream=True,
        )
        
        # 如果不需要清理，直接流式输出
        if not self.clean_output:
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    print(delta.content, end="")
            # 最后打印一个换行，让终端提示符显示在新行
            print()
            return
        
        # 智能流式输出模式，仅在遇到代码块时临时缓存内容
        buffer = ""  # 临时缓冲区
        buffering = False  # 是否正在缓存
        newline_count = 0  # 缓冲区内的换行符计数
        
        for chunk in stream:
            delta = chunk.choices[0].delta
            if not delta.content:
                continue
                
            content = delta.content
            
            # 检查是否包含代码块标记
            if "```" in content or buffering:
                # 如果发现代码块标记或已经在缓存模式，进入缓存模式
                buffering = True
                buffer += content
                
                # 计算缓冲区中的换行符数量
                newline_count += content.count('\n')
                
                # 当缓冲区包含至少2行内容或超过500字符或包含结束标记，处理并输出
                if newline_count >= 2 or len(buffer) > 500 or "```" in buffer and buffer.count("```") >= 2:
                    # 清理代码块标记
                    cleaned_buffer = self._clean_code_blocks(buffer)
                    print(cleaned_buffer, end="")
                    
                    # 重置缓存状态
                    buffer = ""
                    buffering = False
                    newline_count = 0
            else:
                # 正常流式输出
                print(content, end="")
        
        # 处理剩余的缓冲区内容
        if buffer:
            cleaned_buffer = self._clean_code_blocks(buffer)
            print(cleaned_buffer, end="")
        
        # 最后打印一个换行，让终端提示符显示在新行
        print()
    
    def _clean_code_blocks(self, text):
        """清理代码块标记，保留实际内容"""
        # 1. 移除代码块开始标记 ```language
        cleaned_text = re.sub(r'```[\w]*[ \t]*\n?', '', text)
        # 2. 移除代码块结束标记
        cleaned_text = re.sub(r'\n?```', '', cleaned_text)
        # 3. 移除单独一行的代码块标记
        cleaned_text = re.sub(r'^```$', '', cleaned_text, flags=re.MULTILINE)
        return cleaned_text


def main():
    # 创建ShellAI实例
    shell_oiva = ShellOiva()
    
    # 检查是否有命令行参数
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # 获取用户的问题（所有命令行参数组合起来）
    user_query = " ".join(sys.argv[1:])
    
    # 处理用户查询
    shell_oiva.process_query(user_query)


if __name__ == "__main__":
    main()