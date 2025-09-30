# -*- coding: utf-8 -*-
"""
文章数据模型
定义文章相关的数据结构和验证规则
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class ArticleModel(BaseModel):
    """
    文章数据模型
    
    :param title: 文章标题
    :param content: 文章内容
    :param url: 文章链接
    :param source_name: 抓取源名称
    :param score: 文章评分/热度
    :param comments_count: 评论数量
    :param created_at: 创建时间
    :param tags: 文章标签列表
    """
    title: str = Field(..., min_length=1, max_length=500, description="文章标题")
    content: Optional[str] = Field(None, description="文章内容")
    url: HttpUrl = Field(..., description="文章链接")
    source_name: str = Field(..., min_length=1, max_length=50, description="抓取源名称")
    score: Optional[int] = Field(0, ge=0, description="文章评分/热度")
    comments_count: Optional[int] = Field(0, ge=0, description="评论数量")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    tags: Optional[List[str]] = Field(default_factory=list, description="文章标签列表")

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }
        
    def to_text_format(self) -> str:
        """
        转换为文本格式输出
        
        :return: 格式化的文本字符串
        """
        text_lines = [
            f"标题: {self.title}",
            f"链接: {self.url}",
            f"来源: {self.source_name}",
            f"评分: {self.score}",
            f"评论数: {self.comments_count}",
            f"时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if self.content:
            text_lines.append(f"内容: {self.content}")
            
        if self.tags:
            text_lines.append(f"标签: {', '.join(self.tags)}")
            
        text_lines.append("-" * 80)
        
        return "\n".join(text_lines)


class CrawlResult(BaseModel):
    """
    抓取结果模型
    
    :param articles: 抓取到的文章列表
    :param total_count: 总数量
    :param source_name: 抓取源名称
    :param crawl_time: 抓取时间
    :param success: 是否成功
    :param error_message: 错误信息
    """
    articles: List[ArticleModel] = Field(default_factory=list, description="抓取到的文章列表")
    total_count: int = Field(0, ge=0, description="总数量")
    source_name: str = Field(..., description="抓取源名称")
    crawl_time: datetime = Field(default_factory=datetime.now, description="抓取时间")
    success: bool = Field(True, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }