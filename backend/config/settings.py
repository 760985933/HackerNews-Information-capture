# -*- coding: utf-8 -*-
"""
系统配置管理
负责管理系统的各种配置参数
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """
    系统配置类
    管理所有系统配置参数
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        :param config_file: 配置文件路径
        """
        # 加载环境变量
        if config_file and Path(config_file).exists():
            load_dotenv(config_file)
        else:
            load_dotenv()
        
        # 基础配置
        self.DEBUG = self._get_bool_env('DEBUG', False)
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.OUTPUT_DIR = os.getenv('OUTPUT_DIR', '.')
        
        # 抓取配置
        self.DEFAULT_DELAY = self._get_int_env('DEFAULT_DELAY', 1)
        self.DEFAULT_TIMEOUT = self._get_int_env('DEFAULT_TIMEOUT', 30)
        self.MAX_RETRIES = self._get_int_env('MAX_RETRIES', 3)
        
        # 文件管理配置
        self.CLEANUP_DAYS = self._get_int_env('CLEANUP_DAYS', 30)
        self.MAX_FILE_SIZE = self._get_int_env('MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB
        
        # 抓取器配置
        self.CRAWLER_CONFIGS = self._load_crawler_configs()
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """
        获取布尔类型环境变量
        
        :param key: 环境变量键
        :param default: 默认值
        :return: 布尔值
        """
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_int_env(self, key: str, default: int) -> int:
        """
        获取整数类型环境变量
        
        :param key: 环境变量键
        :param default: 默认值
        :return: 整数值
        """
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _load_crawler_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        加载抓取器配置
        
        :return: 抓取器配置字典
        """
        return {
            'hackernews': {
                'max_pages': self._get_int_env('HN_MAX_PAGES', 1),
                'delay': self._get_int_env('HN_DELAY', 1),
                'fetch_content': self._get_bool_env('HN_FETCH_CONTENT', False),
                'timeout': self._get_int_env('HN_TIMEOUT', 30)
            }
        }
    
    def get_crawler_config(self, crawler_name: str) -> Dict[str, Any]:
        """
        获取指定抓取器的配置
        
        :param crawler_name: 抓取器名称
        :return: 配置字典
        """
        return self.CRAWLER_CONFIGS.get(crawler_name, {})
    
    def update_crawler_config(self, crawler_name: str, config: Dict[str, Any]) -> None:
        """
        更新抓取器配置
        
        :param crawler_name: 抓取器名称
        :param config: 新配置
        """
        if crawler_name not in self.CRAWLER_CONFIGS:
            self.CRAWLER_CONFIGS[crawler_name] = {}
        
        self.CRAWLER_CONFIGS[crawler_name].update(config)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        :return: 配置字典
        """
        return {
            'DEBUG': self.DEBUG,
            'LOG_LEVEL': self.LOG_LEVEL,
            'OUTPUT_DIR': self.OUTPUT_DIR,
            'DEFAULT_DELAY': self.DEFAULT_DELAY,
            'DEFAULT_TIMEOUT': self.DEFAULT_TIMEOUT,
            'MAX_RETRIES': self.MAX_RETRIES,
            'CLEANUP_DAYS': self.CLEANUP_DAYS,
            'MAX_FILE_SIZE': self.MAX_FILE_SIZE,
            'CRAWLER_CONFIGS': self.CRAWLER_CONFIGS
        }


# 全局配置实例
settings = Settings()