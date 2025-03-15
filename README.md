# ShellOiva

一个基于命令行的 AI 助手，专注于提供 Windows 命令行工具和脚本解决方案。

## API 兼容性

ShellOiva 完全兼容 OpenAI 格式的 API 接口，这意味着您可以使用以下任何提供商的 API：

- OpenAI (ChatGPT)
- Moonshot AI
- DeepSeek AI 
- Claude API
- 任何其他兼容 OpenAI 格式的 API 服务

只需在 `config.toml` 中修改 `api_key` 和 `base_url` 字段即可切换不同的 API 提供商。示例：

```toml
# OpenAI
api_key = "sk-xxxxxxxx"
base_url = "https://api.openai.com/v1"

# Moonshot AI
api_key = "sk-xxxxxxxx"
base_url = "https://api.moonshot.cn/v1"

# DeepSeek AI
api_key = "xxxxxxxx"
base_url = "https://api.deepseek.com/v1"
```

## 安装

1. 安装依赖项:
   ```
   pip install -r requirements.txt
   ```

2. 配置 `config.toml` 文件（已提供默认配置）:
   - 可以根据需要修改 API 密钥、基础 URL、清理输出选项等

3. 将工具打包为可执行文件:
   ```
   pyinstaller --onefile --name oiva.exe oiva.py
   ```

4. **重要**: 将 `config.toml` 文件复制到 `dist` 目录中，与 `oiva` 放在同一个目录下

5. 将包含 `oiva` 和 `config.toml` 的目录添加到系统环境变量，以便从任何位置访问（例如：`E:\shell-oiva`）
   - Windows: 右键"此电脑" → 属性 → 高级系统设置 → 环境变量 → 在"系统变量"中找到"Path" → 编辑 → 新建 → 添加目录路径

## 使用方法

基本用法:
```
oiva <您的问题>
```

示例:
```
oiva 怎么打印文件列表
oiva 如何查看系统信息
oiva 批量重命名文件
```

## 配置文件说明

配置文件 `config.toml` **必须与可执行文件放在同一目录下**，它包含以下设置:

- **API 设置**:
  - `api_key`: API 密钥
  - `base_url`: API 基础 URL
  - `model`: 使用的模型名称

- **输出设置**:
  - `clean_output`: 是否清理代码块符号，`true` 表示清理，`false` 表示保留原样
  - `temperature`: 控制输出的随机性，值越大输出越随机

- **系统设置**:
  - `prompt`: 系统提示，指导 AI 如何回答问题

## 故障排除

- **找不到配置文件**: 确保 `config.toml` 文件与 `oiva` 在同一目录下
- **API 错误**: 检查 `config.toml` 中的 API 密钥和 URL 是否正确 