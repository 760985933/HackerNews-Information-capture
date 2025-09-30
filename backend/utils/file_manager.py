# -*- coding: utf-8 -*-
"""
文件管理器
负责处理文件输出和管理
"""

import os
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging

from backend.models.article import ArticleModel, CrawlResult


class FileManager:
    """
    文件管理器
    负责将抓取结果输出到文件
    """
    
    def __init__(self, output_dir: str = "."):
        """
        初始化文件管理器
        
        :param output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger("file_manager")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_crawl_result(self, result: CrawlResult) -> Optional[str]:
        """
        保存抓取结果到文件
        
        :param result: 抓取结果
        :return: 输出文件路径或None
        """
        try:
            if not result.success or not result.articles:
                self.logger.warning(f"抓取结果无效或为空: {result.source_name}")
                return None
            
            # 生成文件名（按日期）
            filename = self._generate_filename(result.source_name, result.crawl_time)
            filepath = self.output_dir / filename
            
            # 写入文件
            content = self._format_articles_to_text(result)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"成功保存 {len(result.articles)} 篇文章到: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"保存文件失败: {str(e)}")
            return None
    
    def _generate_filename(self, source_name: str, crawl_time: datetime) -> str:
        """
        生成输出文件名
        
        :param source_name: 抓取源名称
        :param crawl_time: 抓取时间
        :return: 文件名
        """
        date_str = crawl_time.strftime("%Y-%m-%d")
        time_str = crawl_time.strftime("%H%M%S")
        return f"{date_str}_{source_name}_{time_str}_news.txt"
    
    def _format_articles_to_text(self, result: CrawlResult) -> str:
        """
        将文章列表格式化为文本
        
        :param result: 抓取结果
        :return: 格式化的文本内容
        """
        lines = []
        
        # 添加头部信息
        lines.append("=" * 80)
        lines.append(f"IT资讯抓取报告")
        lines.append("=" * 80)
        lines.append(f"抓取源: {result.source_name}")
        lines.append(f"抓取时间: {result.crawl_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"文章总数: {result.total_count}")
        lines.append("=" * 80)
        lines.append("")
        
        # 添加文章内容
        for i, article in enumerate(result.articles, 1):
            lines.append(f"【文章 {i}】")
            lines.append(article.to_text_format())
            lines.append("")
        
        # 添加尾部信息
        lines.append("=" * 80)
        lines.append("报告结束")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_output_files(self, source_name: Optional[str] = None) -> List[str]:
        """
        获取输出文件列表
        
        :param source_name: 可选的抓取源名称过滤
        :return: 文件路径列表
        """
        try:
            pattern = "*_news.txt"
            if source_name:
                pattern = f"*_{source_name}_*_news.txt"
            
            files = list(self.output_dir.glob(pattern))
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return [str(f) for f in files]
            
        except Exception as e:
            self.logger.error(f"获取输出文件列表失败: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        清理旧文件
        
        :param days: 保留天数
        :return: 删除的文件数量
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in self.output_dir.glob("*_news.txt"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    self.logger.info(f"删除旧文件: {file_path}")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理旧文件失败: {str(e)}")
            return 0
    
    def get_file_info(self, filepath: str) -> Optional[dict]:
        """
        获取文件信息
        
        :param filepath: 文件路径
        :return: 文件信息字典或None
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "path": str(path),
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "is_file": path.is_file()
            }
            
        except Exception as e:
            self.logger.error(f"获取文件信息失败 {filepath}: {str(e)}")
            return None