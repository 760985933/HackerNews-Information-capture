# -*- coding: utf-8 -*-
"""
抓取器工厂
负责创建和管理不同类型的抓取器
"""

from typing import Dict, Type, Optional, Any
import logging

from backend.crawlers.base_crawler import BaseCrawler


class CrawlerFactory:
    """
    抓取器工厂类
    使用工厂模式创建和管理抓取器实例
    """
    
    _crawlers: Dict[str, Type[BaseCrawler]] = {}
    _logger = logging.getLogger("crawler.factory")
    
    @classmethod
    def register_crawler(cls, name: str, crawler_class: Type[BaseCrawler]) -> None:
        """
        注册抓取器类
        
        :param name: 抓取器名称
        :param crawler_class: 抓取器类
        """
        if not issubclass(crawler_class, BaseCrawler):
            raise ValueError(f"抓取器类 {crawler_class.__name__} 必须继承自 BaseCrawler")
            
        cls._crawlers[name] = crawler_class
        cls._logger.info(f"注册抓取器: {name}")
    
    @classmethod
    def create_crawler(cls, name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseCrawler]:
        """
        创建抓取器实例
        
        :param name: 抓取器名称
        :param config: 配置参数
        :return: 抓取器实例或None
        """
        if name not in cls._crawlers:
            cls._logger.error(f"未找到抓取器: {name}")
            return None
            
        try:
            crawler_class = cls._crawlers[name]
            crawler = crawler_class(config=config)
            cls._logger.info(f"创建抓取器实例: {name}")
            return crawler
        except Exception as e:
            cls._logger.error(f"创建抓取器失败 {name}: {str(e)}")
            return None
    
    @classmethod
    def get_available_crawlers(cls) -> Dict[str, str]:
        """
        获取所有可用的抓取器
        
        :return: 抓取器名称和描述的字典
        """
        result = {}
        for name, crawler_class in cls._crawlers.items():
            result[name] = crawler_class.__doc__ or f"{name} 抓取器"
        return result
    
    @classmethod
    def is_crawler_available(cls, name: str) -> bool:
        """
        检查抓取器是否可用
        
        :param name: 抓取器名称
        :return: 是否可用
        """
        return name in cls._crawlers