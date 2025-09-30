# -*- coding: utf-8 -*-
"""
Hacker News 抓取器
专门用于抓取 Hacker News 网站的资讯内容
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests

from backend.crawlers.base_crawler import BaseCrawler
from backend.models.article import ArticleModel, CrawlResult


class HackerNewsCrawler(BaseCrawler):
    """
    Hacker News 抓取器
    抓取 https://news.ycombinator.com/front 页面的资讯内容
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Hacker News 抓取器
        
        :param config: 配置参数字典
                      {
                          "max_pages": 1,      # 最大抓取页数
                          "delay": 1,          # 请求延迟（秒）
                          "fetch_content": False,  # 是否抓取文章内容
                          "timeout": 30        # 请求超时时间
                      }
        """
        # 设置默认配置，启用内容抓取
        default_config = {
            "max_pages": 1,
            "delay": 1,
            "fetch_content": True,  # 默认启用内容抓取
            "timeout": 30
        }
        
        # 合并用户配置和默认配置
        if config:
            default_config.update(config)
        
        super().__init__(
            name="hackernews",
            base_url="https://news.ycombinator.com",
            config=default_config
        )
    
    def crawl(self) -> CrawlResult:
        """
        执行 Hacker News 抓取任务
        
        :return: 抓取结果
        """
        try:
            self.logger.info("开始抓取 Hacker News")
            
            # 抓取首页
            url = f"{self.base_url}/news"
            response = self._make_request(url)
            
            if not response:
                return CrawlResult(
                    source_name=self.name,
                    success=False,
                    error_message="无法访问 Hacker News 首页"
                )
            
            # 解析页面
            articles = self.parse_page(response)
            
            self.logger.info(f"成功抓取 {len(articles)} 篇文章")
            
            return CrawlResult(
                articles=articles,
                total_count=len(articles),
                source_name=self.name,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"抓取过程中发生错误: {str(e)}")
            return CrawlResult(
                source_name=self.name,
                success=False,
                error_message=str(e)
            )
    
    def parse_page(self, response: requests.Response) -> List[ArticleModel]:
        """
        解析 Hacker News 页面内容
        
        :param response: HTTP响应对象
        :return: 解析出的文章列表
        """
        articles = []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找所有文章条目
            # Hacker News 使用 .athing 类标识文章行
            article_rows = soup.find_all('tr', class_='athing')
            
            for row in article_rows:
                try:
                    article = self._parse_article_row(row, soup)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"解析文章行时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"解析页面时出错: {str(e)}")
            
        return articles
    
    def _parse_article_row(self, row, soup: BeautifulSoup) -> Optional[ArticleModel]:
        """
        解析单个文章行
        
        :param row: 文章行元素
        :param soup: BeautifulSoup对象
        :return: 文章模型或None
        """
        try:
            # 获取文章ID
            article_id = row.get('id')
            if not article_id:
                self.logger.debug("文章行缺少ID属性")
                return None
            
            # 查找标题链接
            title_cell = row.find('span', class_='titleline')
            if not title_cell:
                self.logger.debug(f"文章 {article_id} 未找到titleline元素")
                return None
                
            title_link = title_cell.find('a')
            if not title_link:
                self.logger.debug(f"文章 {article_id} 未找到标题链接")
                return None
                
            title = title_link.get_text(strip=True)
            url = title_link.get('href', '')
            
            # 处理相对链接
            if url.startswith('item?id='):
                url = f"{self.base_url}/{url}"
            elif url.startswith('/'):
                url = f"{self.base_url}{url}"
            
            # 查找对应的元数据行（下一行）
            meta_row = row.find_next_sibling('tr')
            score = 0
            comments_count = 0
            
            if meta_row:
                # 查找subtext元素
                subtext = meta_row.find('td', class_='subtext')
                if subtext:
                    # 查找评分
                    score_span = subtext.find('span', class_='score')
                    if score_span:
                        score_text = score_span.get_text(strip=True)
                        score_match = re.search(r'(\d+)', score_text)
                        if score_match:
                            score = int(score_match.group(1))
                            self.logger.debug(f"文章 {article_id} 评分: {score}")
                    else:
                        self.logger.debug(f"文章 {article_id} 未找到评分信息")
                    
                    # 查找评论数 - 查找所有链接，找到包含"comments"的链接
                    links = subtext.find_all('a')
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        # 查找评论链接：包含item?id=且文本包含comment
                        if 'item?id=' in href and 'comment' in text.lower():
                            comments_match = re.search(r'(\d+)', text)
                            if comments_match:
                                comments_count = int(comments_match.group(1))
                                self.logger.debug(f"文章 {article_id} 评论数: {comments_count}")
                                break
                    
                    if comments_count == 0:
                        self.logger.debug(f"文章 {article_id} 未找到评论数信息")
                else:
                    self.logger.debug(f"文章 {article_id} 未找到subtext元素")
            else:
                self.logger.debug(f"文章 {article_id} 未找到元数据行")
            
            # 获取文章内容（如果配置要求）
            content = None
            if self.config.get('fetch_content', False):
                content = self._fetch_article_content(url)
            
            # 创建文章模型
            article = ArticleModel(
                title=title,
                content=content,
                url=url,
                source_name=self.name,
                score=score,
                comments_count=comments_count,
                created_at=datetime.now()
            )
            
            self.logger.debug(f"成功解析文章: {title} (评分: {score}, 评论: {comments_count})")
            return article
            
        except Exception as e:
            self.logger.warning(f"解析文章行失败 (ID: {article_id if 'article_id' in locals() else 'unknown'}): {str(e)}")
            return None
    
    def _fetch_article_content(self, url: str) -> Optional[str]:
        """
        获取文章内容
        
        :param url: 文章URL
        :return: 文章内容或None
        """
        try:
            # 添加延迟避免过于频繁的请求
            self._delay_between_requests()
            
            # 添加更完整的请求头，避免被反爬虫机制拦截
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"HTTP {response.status_code} for {url}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 检查是否遇到验证页面或反爬虫机制
            page_text = soup.get_text().lower()
            if any(keyword in page_text for keyword in ['just a moment', '验证', 'verify', 'cloudflare', 'checking your browser']):
                self.logger.warning(f"检测到反爬虫机制: {url}")
                return "内容无法获取：网站启用了反爬虫保护"
            
            # 使用网站特定的内容提取策略
            content = self._extract_content_by_site(url, soup)
            if content:
                return content
            
            # 通用内容提取策略
            content = self._extract_content_generic(soup)
            if content:
                return content
                
            self.logger.debug(f"无法提取内容: {url}")
            return None
            
        except requests.exceptions.Timeout:
            self.logger.warning(f"请求超时: {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"请求失败 {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.warning(f"获取文章内容失败 {url}: {str(e)}")
            return None
    
    def _extract_content_by_site(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        """
        根据网站特定结构提取内容
        
        :param url: 文章URL
        :param soup: BeautifulSoup对象
        :return: 提取的内容或None
        """
        try:
            # Anthropic网站
            if 'anthropic.com' in url:
                # 优先尝试article标签
                article_elem = soup.find('article')
                if article_elem:
                    # 移除导航和其他非内容元素
                    for elem in article_elem.find_all(['nav', 'header', 'footer', 'aside']):
                        elem.decompose()
                    
                    content = article_elem.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        # 清理内容，移除多余空白
                        content = ' '.join(content.split())
                        # 限制内容长度，但保持完整性
                        if len(content) > 3000:
                            content = content[:3000] + "..."
                        return content
            
            # GitHub网站
            elif 'github.com' in url:
                readme_elem = soup.find('article', class_='markdown-body')
                if readme_elem:
                    content = readme_elem.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        content = ' '.join(content.split())
                        if len(content) > 2000:
                            content = content[:2000] + "..."
                        return content
            
            # NPM网站 - 处理反爬虫情况
            elif 'npmjs.com' in url:
                # 如果遇到验证页面，返回特殊提示
                if soup.title and 'just a moment' in soup.title.get_text().lower():
                    return "NPM包页面：由于反爬虫保护，无法直接获取内容。请访问链接查看详情。"
                
                # 尝试提取包描述
                desc_elem = soup.find('p', {'data-testid': 'description'}) or soup.find('.package-description')
                if desc_elem:
                    return desc_elem.get_text(strip=True)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"网站特定内容提取失败 {url}: {str(e)}")
            return None
    
    def _extract_content_generic(self, soup: BeautifulSoup) -> Optional[str]:
        """
        通用内容提取策略
        
        :param soup: BeautifulSoup对象
        :return: 提取的内容或None
        """
        try:
            # 按优先级尝试不同的选择器
            content_selectors = [
                ('article', 500),  # 文章标签，最高优先级
                ('main', 300),     # 主内容区域
                ('.post-content', 400),
                ('.entry-content', 400),
                ('.content', 200),
                ('.markdown-body', 400),
                ('.prose', 300),
                ('div[role="main"]', 300),
            ]
            
            best_content = None
            best_score = 0
            
            for selector, base_score in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    # 移除脚本、样式等非内容元素
                    for tag in elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        tag.decompose()
                    
                    content = elem.get_text(separator=' ', strip=True)
                    if len(content) < 100:  # 内容太短，跳过
                        continue
                    
                    # 计算内容质量分数
                    score = base_score + min(len(content) // 10, 200)  # 长度加分，但有上限
                    
                    if score > best_score:
                        best_content = content
                        best_score = score
            
            if best_content:
                # 清理和格式化内容
                best_content = ' '.join(best_content.split())
                
                # 智能截断：尝试在句子结束处截断
                if len(best_content) > 2500:
                    truncate_pos = 2500
                    # 寻找最近的句号、问号或感叹号
                    for i in range(truncate_pos, max(truncate_pos - 200, 0), -1):
                        if best_content[i] in '.!?':
                            truncate_pos = i + 1
                            break
                    best_content = best_content[:truncate_pos]
                    if not best_content.endswith('...'):
                        best_content += "..."
                
                return best_content
            
            # 最后尝试：收集所有段落
            paragraphs = soup.find_all('p')
            if paragraphs:
                content_parts = []
                total_length = 0
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20 and total_length < 2000:  # 过滤太短的段落
                        content_parts.append(text)
                        total_length += len(text)
                
                if content_parts:
                    content = ' '.join(content_parts)
                    if len(content) > 100:
                        return content
            
            return None
            
        except Exception as e:
            self.logger.debug(f"通用内容提取失败: {str(e)}")
            return None
    
    def validate_config(self) -> bool:
        """
        验证配置参数
        
        :return: 配置是否有效
        """
        try:
            max_pages = self.config.get('max_pages', 1)
            delay = self.config.get('delay', 1)
            
            if not isinstance(max_pages, int) or max_pages < 1:
                self.logger.error("max_pages 必须是大于0的整数")
                return False
                
            if not isinstance(delay, (int, float)) or delay < 0:
                self.logger.error("delay 必须是非负数")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {str(e)}")
            return False