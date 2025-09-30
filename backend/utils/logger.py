# -*- coding: utf-8 -*-
"""
日志管理器
负责配置和管理系统日志
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class LoggerManager:
    """
    日志管理器
    负责配置和管理系统的日志记录
    """
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        初始化日志管理器
        
        :param log_dir: 日志目录
        :param log_level: 日志级别
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        配置日志系统
        """
        # 创建根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器 - 主日志文件
        main_log_file = self.log_dir / "crawler.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志文件
        error_log_file = self.log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志器
        
        :param name: 日志器名称
        :return: 日志器实例
        """
        return logging.getLogger(name)
    
    def create_crawler_logger(self, crawler_name: str) -> logging.Logger:
        """
        为抓取器创建专用日志器
        
        :param crawler_name: 抓取器名称
        :return: 日志器实例
        """
        logger_name = f"crawler.{crawler_name}"
        logger = logging.getLogger(logger_name)
        
        # 如果已经配置过，直接返回
        if logger.handlers:
            return logger
        
        # 创建抓取器专用日志文件
        crawler_log_file = self.log_dir / f"{crawler_name}.log"
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            crawler_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.setLevel(self.log_level)
        
        return logger
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        清理旧日志文件
        
        :param days: 保留天数
        :return: 删除的文件数量
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"清理旧日志文件失败: {str(e)}")
            return 0
    
    def get_log_files(self) -> list:
        """
        获取所有日志文件列表
        
        :return: 日志文件路径列表
        """
        try:
            log_files = list(self.log_dir.glob("*.log"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(f) for f in log_files]
        except Exception as e:
            logging.error(f"获取日志文件列表失败: {str(e)}")
            return []
    
    def set_log_level(self, level: str) -> None:
        """
        设置日志级别
        
        :param level: 日志级别字符串
        """
        try:
            new_level = getattr(logging, level.upper(), logging.INFO)
            self.log_level = new_level
            
            # 更新所有处理器的日志级别
            root_logger = logging.getLogger()
            root_logger.setLevel(new_level)
            
            for handler in root_logger.handlers:
                if not isinstance(handler, logging.handlers.RotatingFileHandler) or "error.log" not in str(handler.baseFilename):
                    handler.setLevel(new_level)
                    
        except Exception as e:
            logging.error(f"设置日志级别失败: {str(e)}")


# 全局日志管理器实例
logger_manager = LoggerManager()