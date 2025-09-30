#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT资讯抓取系统主程序
负责协调各个模块，执行抓取任务
"""

import sys
import argparse
from typing import Optional, Dict, Any
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.config.settings import settings
from backend.utils.logger import logger_manager
from backend.utils.file_manager import FileManager
from backend.crawlers.crawler_factory import CrawlerFactory
from backend.crawlers.hackernews_crawler import HackerNewsCrawler


class NewsAggregator:
    """
    新闻聚合器主类
    负责协调整个抓取流程
    """
    
    def __init__(self):
        """
        初始化新闻聚合器
        """
        # 初始化日志系统
        self.logger = logger_manager.get_logger("main")
        
        # 初始化文件管理器
        self.file_manager = FileManager(settings.OUTPUT_DIR)
        
        # 注册抓取器
        self._register_crawlers()
        
        self.logger.info("IT资讯抓取系统初始化完成")
    
    def _register_crawlers(self) -> None:
        """
        注册所有可用的抓取器
        """
        try:
            CrawlerFactory.register_crawler("hackernews", HackerNewsCrawler)
            self.logger.info("抓取器注册完成")
        except Exception as e:
            self.logger.error(f"抓取器注册失败: {str(e)}")
            raise
    
    def run_crawler(self, crawler_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        运行指定的抓取器
        
        :param crawler_name: 抓取器名称
        :param config: 可选的配置参数
        :return: 是否成功
        """
        try:
            self.logger.info(f"开始运行抓取器: {crawler_name}")
            
            # 获取抓取器配置
            crawler_config = settings.get_crawler_config(crawler_name)
            if config:
                crawler_config.update(config)
            
            # 创建抓取器实例
            crawler = CrawlerFactory.create_crawler(crawler_name, crawler_config)
            if not crawler:
                self.logger.error(f"无法创建抓取器: {crawler_name}")
                return False
            
            # 验证配置
            if not crawler.validate_config():
                self.logger.error(f"抓取器配置无效: {crawler_name}")
                return False
            
            # 执行抓取
            with crawler:
                result = crawler.crawl()
                
                if not result.success:
                    self.logger.error(f"抓取失败: {result.error_message}")
                    return False
                
                # 保存结果
                output_file = self.file_manager.save_crawl_result(result)
                if output_file:
                    self.logger.info(f"抓取完成，结果已保存到: {output_file}")
                    print(f"✅ 抓取完成！结果已保存到: {output_file}")
                    print(f"📊 共抓取 {result.total_count} 篇文章")
                    return True
                else:
                    self.logger.error("保存抓取结果失败")
                    return False
                    
        except Exception as e:
            self.logger.error(f"运行抓取器时发生错误: {str(e)}")
            print(f"❌ 抓取失败: {str(e)}")
            return False
    
    def list_crawlers(self) -> None:
        """
        列出所有可用的抓取器
        """
        crawlers = CrawlerFactory.get_available_crawlers()
        
        print("📋 可用的抓取器:")
        print("-" * 50)
        
        for name, description in crawlers.items():
            print(f"  • {name}: {description}")
        
        print("-" * 50)
        print(f"总计: {len(crawlers)} 个抓取器")
    
    def show_config(self) -> None:
        """
        显示当前配置
        """
        config = settings.to_dict()
        
        print("⚙️  当前系统配置:")
        print("-" * 50)
        
        for key, value in config.items():
            if key == 'CRAWLER_CONFIGS':
                print(f"  {key}:")
                for crawler_name, crawler_config in value.items():
                    print(f"    {crawler_name}:")
                    for config_key, config_value in crawler_config.items():
                        print(f"      {config_key}: {config_value}")
            else:
                print(f"  {key}: {value}")
        
        print("-" * 50)
    
    def cleanup_files(self, days: int = None) -> None:
        """
        清理旧文件
        
        :param days: 保留天数，默认使用配置值
        """
        days = days or settings.CLEANUP_DAYS
        
        try:
            deleted_count = self.file_manager.cleanup_old_files(days)
            log_deleted_count = logger_manager.cleanup_old_logs(days)
            
            print(f"🧹 清理完成:")
            print(f"  • 删除了 {deleted_count} 个旧的输出文件")
            print(f"  • 删除了 {log_deleted_count} 个旧的日志文件")
            
        except Exception as e:
            self.logger.error(f"清理文件时发生错误: {str(e)}")
            print(f"❌ 清理失败: {str(e)}")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    :return: 参数解析器
    """
    parser = argparse.ArgumentParser(
        description="IT资讯抓取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py run hackernews                    # 运行Hacker News抓取器
  python main.py run hackernews --delay 2          # 设置请求延迟为2秒
  python main.py list                              # 列出所有可用抓取器
  python main.py config                            # 显示当前配置
  python main.py cleanup                           # 清理旧文件
  python main.py cleanup --days 7                  # 清理7天前的文件
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='运行抓取器')
    run_parser.add_argument('crawler', help='抓取器名称')
    run_parser.add_argument('--delay', type=int, help='请求间延迟秒数')
    run_parser.add_argument('--max-pages', type=int, help='最大抓取页数')
    run_parser.add_argument('--fetch-content', action='store_true', help='是否抓取文章内容')
    run_parser.add_argument('--timeout', type=int, help='请求超时时间')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有可用抓取器')
    
    # config 命令
    subparsers.add_parser('config', help='显示当前配置')
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧文件')
    cleanup_parser.add_argument('--days', type=int, help='保留天数')
    
    return parser


def main():
    """
    主函数
    """
    try:
        # 解析命令行参数
        parser = create_argument_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # 创建新闻聚合器实例
        aggregator = NewsAggregator()
        
        # 执行相应命令
        if args.command == 'run':
            # 构建配置参数
            config = {}
            if args.delay is not None:
                config['delay'] = args.delay
            if args.max_pages is not None:
                config['max_pages'] = args.max_pages
            if args.fetch_content:
                config['fetch_content'] = True
            if args.timeout is not None:
                config['timeout'] = args.timeout
            
            # 运行抓取器
            success = aggregator.run_crawler(args.crawler, config if config else None)
            sys.exit(0 if success else 1)
            
        elif args.command == 'list':
            aggregator.list_crawlers()
            
        elif args.command == 'config':
            aggregator.show_config()
            
        elif args.command == 'cleanup':
            aggregator.cleanup_files(args.days)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()