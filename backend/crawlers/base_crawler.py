# -*- coding: utf-8 -*-
"""
抓取器基类
定义抓取器的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.models.article import ArticleModel, CrawlResult


class BaseCrawler(ABC):
    """
    抓取器基类
    定义所有抓取器必须实现的接口
    """
    
    def __init__(self, name: str, base_url: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化抓取器
        
        :param name: 抓取器名称
        :param base_url: 基础URL
        :param config: 配置参数
        """
        self.name = name
        self.base_url = base_url
        self.config = config or {}
        self.logger = logging.getLogger(f"crawler.{name}")
        
        # 初始化HTTP会话
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        创建HTTP会话，配置重试策略和超时
        
        :return: 配置好的requests会话
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置请求头
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """
        发起HTTP请求，包含错误处理
        
        :param url: 请求URL
        :param timeout: 超时时间
        :return: 响应对象或None
        """
        try:
            self.logger.info(f"正在请求: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败 {url}: {str(e)}")
            return None
    
    def _delay_between_requests(self) -> None:
        """
        请求间延迟，避免过于频繁的请求
        """
        delay = self.config.get('delay', 1)
        if delay > 0:
            time.sleep(delay)
    
    @abstractmethod
    def crawl(self) -> CrawlResult:
        """
        执行抓取任务
        
        :return: 抓取结果
        """
        pass
    
    @abstractmethod
    def parse_page(self, response: requests.Response) -> List[ArticleModel]:
        """
        解析页面内容
        
        :param response: HTTP响应对象
        :return: 解析出的文章列表
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置参数
        
        :return: 配置是否有效
        """
        return True
    
    def get_source_info(self) -> Dict[str, Any]:
        """
        获取抓取源信息
        
        :return: 抓取源信息字典
        """
        return {
            "name": self.name,
            "base_url": self.base_url,
            "config": self.config,
            "description": self.__doc__ or f"{self.name} 抓取器"
        }
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        if hasattr(self, 'session'):
            self.session.close()
            
    def __enter__(self):
        """上下文管理器入口"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()