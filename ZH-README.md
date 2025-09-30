# IT资讯抓取系统

一个模块化、可扩展的IT资讯抓取系统，支持从多个资讯网站抓取内容并输出到文本文件。

## 功能特点

- 🔧 **模块化设计**: 采用工厂模式，易于扩展新的抓取器
- 📰 **多源支持**: 目前支持Hacker News，后续可轻松添加其他资讯源
- 📁 **文件输出**: 按日期自动生成文本文件，便于管理
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- 📊 **日志记录**: 详细的日志记录，便于调试和监控
- ⚙️ **配置管理**: 灵活的配置系统，支持环境变量

## 项目结构

```
IT资讯播报/
├── backend/                    # 后端代码
│   ├── crawlers/              # 抓取器模块
│   │   ├── base_crawler.py    # 抓取器基类
│   │   ├── crawler_factory.py # 抓取器工厂
│   │   └── hackernews_crawler.py # Hacker News抓取器
│   ├── models/                # 数据模型
│   │   └── article.py         # 文章数据模型
│   ├── utils/                 # 工具模块
│   │   ├── file_manager.py    # 文件管理器
│   │   └── logger.py          # 日志管理器
│   └── config/                # 配置模块
│       └── settings.py        # 系统配置
├── logs/                      # 日志文件目录
├── venv/                      # Python虚拟环境
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖包列表
├── .env.example              # 配置文件示例
└── README.md                 # 项目说明
```

## 安装和使用

### 1. 环境准备

确保系统已安装Python 3.9+：

```bash
python3 --version
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置系统（可选）

复制配置文件模板并根据需要修改：

```bash
cp .env.example .env
```

### 5. 运行抓取器

```bash
# 运行Hacker News抓取器
python main.py run hackernews

# 设置请求延迟为2秒
python main.py run hackernews --delay 2

# 同时抓取文章内容
python main.py run hackernews --fetch-content

# 查看所有可用抓取器
python main.py list

# 查看当前配置
python main.py config

# 清理30天前的旧文件
python main.py cleanup

# 清理7天前的旧文件
python main.py cleanup --days 7
```

## 命令行参数

### 基本命令

- `run <crawler_name>`: 运行指定的抓取器
- `list`: 列出所有可用的抓取器
- `config`: 显示当前系统配置
- `cleanup`: 清理旧文件和日志

### run 命令参数

- `--delay <seconds>`: 设置请求间延迟时间（秒）
- `--max-pages <number>`: 设置最大抓取页数
- `--fetch-content`: 是否抓取文章详细内容
- `--timeout <seconds>`: 设置请求超时时间

### cleanup 命令参数

- `--days <number>`: 设置文件保留天数

## 配置说明

系统支持通过环境变量或`.env`文件进行配置：

```bash
# 基础配置
DEBUG=false                    # 调试模式
LOG_LEVEL=INFO                # 日志级别
OUTPUT_DIR=.                  # 输出目录

# 抓取配置
DEFAULT_DELAY=1               # 默认请求延迟
DEFAULT_TIMEOUT=30            # 默认超时时间
MAX_RETRIES=3                 # 最大重试次数

# 文件管理
CLEANUP_DAYS=30               # 文件保留天数
MAX_FILE_SIZE=10485760        # 最大文件大小

# Hacker News配置
HN_MAX_PAGES=1                # 最大抓取页数
HN_DELAY=1                    # 请求延迟
HN_FETCH_CONTENT=false        # 是否抓取内容
HN_TIMEOUT=30                 # 请求超时
```

## 输出格式

抓取结果会保存为按日期命名的文本文件，格式如下：

```
2024-01-15_hackernews_143022_news.txt
```

文件内容包含：
- 抓取报告头部信息
- 每篇文章的详细信息（标题、链接、评分、评论数等）
- 报告尾部信息

## 扩展新的抓取器

要添加新的抓取器，请按以下步骤操作：

### 1. 创建抓取器类

在`backend/crawlers/`目录下创建新的抓取器文件：

```python
from backend.crawlers.base_crawler import BaseCrawler
from backend.models.article import ArticleModel, CrawlResult

class NewSiteCrawler(BaseCrawler):
    def __init__(self, config=None):
        super().__init__(
            name="newsite",
            base_url="https://example.com",
            config=config
        )
    
    def crawl(self) -> CrawlResult:
        # 实现抓取逻辑
        pass
    
    def parse_page(self, response) -> List[ArticleModel]:
        # 实现页面解析逻辑
        pass
```

### 2. 注册抓取器

在`main.py`的`_register_crawlers`方法中添加：

```python
CrawlerFactory.register_crawler("newsite", NewSiteCrawler)
```

### 3. 添加配置（可选）

在`backend/config/settings.py`中添加相应配置。

## 日志系统

系统提供完整的日志记录功能：

- `logs/crawler.log`: 主日志文件
- `logs/error.log`: 错误日志文件
- `logs/{crawler_name}.log`: 各抓取器专用日志

日志文件支持自动轮转，避免文件过大。

## 错误处理

系统包含多层错误处理机制：

1. **网络错误**: 自动重试机制，支持指数退避
2. **解析错误**: 跳过有问题的条目，继续处理其他内容
3. **文件错误**: 详细的错误日志记录
4. **配置错误**: 启动时验证配置参数

## 开发规范

本项目遵循以下开发规范：

- 使用类型注解提高代码可读性
- 完整的函数和类注释
- 遵循PEP 8代码风格
- 模块化设计，职责分离
- 完善的错误处理和日志记录

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！