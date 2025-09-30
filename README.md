# IT News Crawling System

A modular and extensible IT news crawling system that supports fetching content from multiple news websites and outputting to text files.

## Features

- 🔧 **Modular Design**: Uses factory pattern for easy extension of new crawlers
- 📰 **Multi-source Support Support Support**: Currently supports Hacker News, with easy extensibility for other news sources
- 📁 **File Output**: Automatically generates date-based text files for easy management
- 🛡️ **Error Handling**: Comprehensive error handling and retry mechanisms
- 📊 **Logging**: Detailed logging for debugging and monitoring
- ⚙️ **Configuration Management**: Flexible configuration system with environment variable support

## Project Structure

```
IT News Broadcast/
├── backend/                    # Backend code
│   ├── crawlers/              # Crawler modules
│   │   ├── base_crawler.py    # Base crawler class
│   │   ├── crawler_factory.py # Crawler factory
│   │   └── hackernews_crawler.py # Hacker News crawler
│   ├── models/                # Data models
│   │   └── article.py         # Article data model
│   ├── utils/                 # Utility modules
│   │   ├── file_manager.py    # File manager
│   │   └── logger.py          # Log manager
│   └── config/                # Configuration module
│       └── settings.py        # System configuration
├── logs/                      # Log files directory
├── venv/                      # Python virtual environment
├── main.py                    # Main program entry
├── requirements.txt           # Dependencies list
├── .env.example              # Configuration file example
└── README.md                 # Project description
```

## Installation and Usage

### 1. Environment Preparation

Ensure Python 3.9+ is installed on your system:

```bash
python3 --version
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure System (Optional)

Copy the configuration template and modify as needed:

```bash
cp .env.example .env
```

### 5. Run the Crawler

```bash
# Run Hacker News crawler
python main.py run hackernews

# Set request delay to 2 seconds
python main.py run hackernews --delay 2

# Fetch article content as well
python main.py run hackernews --fetch-content

# List all available crawlers
python main.py list

# View current configuration
python main.py config

# Clean up files older than 30 days
python main.py cleanup

# Clean up files older than 7 days
python main.py cleanup --days 7
```

## Command Line Arguments

### Basic Commands

- `run <crawler_name>`: Run the specified crawler
- `list`: List all available crawlers
- `config`: Display current system configuration
- `cleanup`: Clean up old files and logs

### Run Command Parameters

- `--delay <seconds>`: Set delay between requests (seconds)
- `--max-pages <number>`: Set maximum number of pages to crawl
- `--fetch-content`: Whether to fetch full article content
- `--timeout <seconds>`: Set request timeout

### Cleanup Command Parameters

- `--days <number>`: Set number of days to keep files

## Configuration Description

The system supports configuration through environment variables or `.env` file:

```bash
# Basic configuration
DEBUG=false                    # Debug mode
LOG_LEVEL=INFO                # Log level
OUTPUT_DIR=.                  # Output directory

# Crawling configuration
DEFAULT_DELAY=1               # Default request delay
DEFAULT_TIMEOUT=30            # Default timeout
MAX_RETRIES=3                 # Maximum retries

# File management
CLEANUP_DAYS=30               # Days to keep files
MAX_FILE_SIZE=10485760        # Maximum file size

# Hacker News configuration
HN_MAX_PAGES=1                # Maximum pages to crawl
HN_DELAY=1                    # Request delay
HN_FETCH_CONTENT=false        # Whether to fetch content
HN_TIMEOUT=30                 # Request timeout
```

## Output Format

Crawling results are saved as date-named text files in the following format:

```
2024-01-15_hackernews_143022_news.txt
```

File content includes:
- Crawling report header information
- Detailed information for each article (title, link, score, comment count, etc.)
- Report footer information

## Extending with New Crawlers

To add a new crawler, follow these steps:

### 1. Create Crawler Class

Create a new crawler file in the `backend/crawlers/` directory:

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
        # Implement crawling logic
        pass
    
    def parse_page(self, response) -> List[ArticleModel]:
        # Implement page parsing logic
        pass
```

### 2. Register the Crawler

Add to the `_register_crawlers` method in `main.py`:

```python
CrawlerFactory.register_crawler("newsite", NewSiteCrawler)
```

### 3. Add Configuration (Optional)

Add corresponding configuration in `backend/config/settings.py`.

## Logging System

The system provides comprehensive logging functionality:

- `logs/crawler.log`: Main log file
- `logs/error.log`: Error log file
- `logs/{crawler_name}.log`: Crawler-specific logs

Log files support automatic rotation to prevent oversized files.

## Error Handling

The system includes multiple layers of error handling:

1. **Network Errors**: Automatic retry mechanism with exponential backoff
2. **Parsing Errors**: Skip problematic items and continue processing others
3. **File Errors**: Detailed error logging
4. **Configuration Errors**: Validate configuration parameters on startup

## Development Standards

This project follows these development standards:

- Use type annotations to improve code readability
- Complete function and class comments
- Follow PEP 8 code style
- Modular design with separation of concerns
- Comprehensive error handling and logging

## License

This project is licensed under the MIT License.

## Contributions

Issues and Pull Requests are welcome to improve this project!
