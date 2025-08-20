# JetBrains License Auto Crawler

这是一个自动爬取JetBrains激活码的高级程序，具有完整的错误处理、日志记录、配置管理等功能。适用于JetBrains的IDEA等其他应用，主要通过GitHub的自动化脚本Actions进行每天的抓取。

This is an advanced program that automatically crawls JetBrains activation codes with comprehensive error handling, logging, configuration management and other features. It is suitable for JetBrains IDEA and other applications, mainly using GitHub's automated scripts Actions for daily crawling.

## Features / 功能特性

- 🔧 **配置管理**: JSON配置文件支持，可自定义所有参数
- 📝 **日志记录**: 详细的日志记录，支持文件和控制台输出
- 🔄 **重试机制**: 智能重试机制，处理网络异常
- ✅ **数据验证**: 激活码格式验证和去重
- 🎯 **命令行界面**: 丰富的命令行参数支持
- 📊 **进度跟踪**: 详细的执行状态和统计信息
- 🛡️ **异常处理**: 完善的错误处理和异常捕获

## Installation / 安装

```bash
# 克隆仓库
git clone <repository-url>
cd AutoJetBrainsLicense

# 安装依赖
pip install -r requirements.txt
```

## Usage / 使用方法

### 基本使用
```bash
python AutoJetBrainsLicense.py
```

### 高级使用
```bash
# 使用自定义URL和输出文件
python AutoJetBrainsLicense.py --url https://example.com --output custom_licenses.txt

# 启用详细日志
python AutoJetBrainsLicense.py --verbose

# 启用调试模式
python AutoJetBrainsLicense.py --debug

# 使用自定义配置文件
python AutoJetBrainsLicense.py --config my_config.json

# 生成默认配置文件
python AutoJetBrainsLicense.py --generate-config
```

## Configuration / 配置

程序支持通过JSON配置文件进行详细配置。默认配置文件为 `config.json`：

```json
{
  "target_url": "https://www.idejihuo.com/",
  "output_file": "JetBrainsLicense.txt",
  "timeout": 30,
  "max_retries": 3,
  "retry_delay": 1,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "log_level": "INFO",
  "log_file": "crawler.log",
  "validate_licenses": true,
  "min_license_length": 10
}
```

## Output / 输出

程序会生成包含激活码的文件，格式如下：
```
# JetBrains License Keys
# Generated on: 2024-01-15 10:30:45
# Total count: 25
# Source: https://www.idejihuo.com/

LICENSE-KEY-1
LICENSE-KEY-2
...
```

## Requirements / 依赖

- Python 3.7+
- requests>=2.28.0
- beautifulsoup4>=4.11.0
- urllib3>=1.26.0
