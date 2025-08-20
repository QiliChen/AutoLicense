# -*- coding: utf-8 -*-
"""
JetBrains License Auto Crawler
自动爬取JetBrains激活码的程序

Author: Auto License Crawler
Description: This program automatically crawls JetBrains activation codes from specified websites.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Set, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class LicenseCrawlerConfig:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "target_url": "https://www.idejihuo.com/",
            "output_file": "JetBrainsLicense.txt",
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "log_level": "INFO",
            "log_file": "crawler.log",
            "validate_licenses": True,
            "min_license_length": 10
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**self.default_config, **config}
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Failed to load config file: {e}. Using default config.")
        return self.default_config.copy()
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save config file: {e}")


class JetBrainsLicenseCrawler:
    """JetBrains激活码爬虫类"""
    
    def __init__(self, config: Optional[LicenseCrawlerConfig] = None):
        self.config = config or LicenseCrawlerConfig()
        self.session = self._create_session()
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """设置日志记录"""
        log_level = getattr(logging, self.config.config["log_level"].upper(), logging.INFO)
        
        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 设置根日志器
        logger = logging.getLogger()
        logger.setLevel(log_level)
        
        # 清除现有的处理器
        logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        if self.config.config["log_file"]:
            try:
                file_handler = logging.FileHandler(
                    self.config.config["log_file"], 
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except IOError as e:
                logging.warning(f"Failed to create log file handler: {e}")
    
    def _create_session(self) -> requests.Session:
        """创建带重试机制的HTTP会话"""
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=self.config.config["max_retries"],
            backoff_factor=self.config.config["retry_delay"],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置请求头
        session.headers.update({
            'User-Agent': self.config.config["user_agent"],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def _is_valid_license(self, license_text: str) -> bool:
        """验证激活码格式"""
        if not license_text or len(license_text.strip()) < self.config.config["min_license_length"]:
            return False
        
        # 基本格式验证：包含字母和数字，可能包含连字符
        license_pattern = re.compile(r'^[A-Z0-9\-]{10,}$', re.IGNORECASE)
        return bool(license_pattern.match(license_text.strip()))
    
    def fetch_licenses(self, url: Optional[str] = None) -> Set[str]:
        """
        从指定URL获取激活码
        
        Args:
            url: 目标URL，如果为None则使用配置中的URL
            
        Returns:
            包含激活码的集合
            
        Raises:
            requests.RequestException: 网络请求异常
            Exception: 其他异常
        """
        target_url = url or self.config.config["target_url"]
        logging.info(f"Starting to crawl licenses from: {target_url}")
        
        unique_licenses = set()
        
        try:
            # 发送HTTP请求
            response = self.session.get(
                target_url, 
                timeout=self.config.config["timeout"]
            )
            response.raise_for_status()
            
            logging.info(f"Successfully fetched webpage. Status code: {response.status_code}")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有input元素
            inputs = soup.find_all('input')
            logging.info(f"Found {len(inputs)} input elements")
            
            for input_element in inputs:
                value = input_element.get('value')
                if value is not None:
                    value = value.strip()
                    if self.config.config["validate_licenses"]:
                        if self._is_valid_license(value):
                            unique_licenses.add(value)
                            logging.debug(f"Added valid license: {value[:10]}...")
                    else:
                        unique_licenses.add(value)
            
            # 也尝试从其他可能的元素中提取激活码
            text_elements = soup.find_all(['p', 'div', 'span', 'td'])
            for element in text_elements:
                text = element.get_text(strip=True)
                if text and self._is_valid_license(text):
                    unique_licenses.add(text)
                    logging.debug(f"Added license from text: {text[:10]}...")
            
            logging.info(f"Successfully extracted {len(unique_licenses)} unique licenses")
            return unique_licenses
            
        except requests.exceptions.Timeout:
            logging.error(f"Request timeout after {self.config.config['timeout']} seconds")
            raise
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching licenses: {e}")
            raise
    
    def save_licenses(self, licenses: Set[str], output_file: Optional[str] = None) -> bool:
        """
        保存激活码到文件
        
        Args:
            licenses: 激活码集合
            output_file: 输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            保存是否成功
        """
        if not licenses:
            logging.warning("No licenses to save")
            return False
        
        output_path = output_file or self.config.config["output_file"]
        
        try:
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 按字母顺序排序激活码
            sorted_licenses = sorted(licenses)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                # 写入文件头
                file.write(f"# JetBrains License Keys\n")
                file.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"# Total count: {len(sorted_licenses)}\n")
                file.write(f"# Source: {self.config.config['target_url']}\n\n")
                
                # 写入激活码
                for license_key in sorted_licenses:
                    file.write(f"{license_key}\n")
            
            logging.info(f"Successfully saved {len(licenses)} licenses to {output_path}")
            return True
            
        except IOError as e:
            logging.error(f"Failed to save licenses to {output_path}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while saving licenses: {e}")
            return False
    
    def run(self, url: Optional[str] = None, output_file: Optional[str] = None) -> bool:
        """
        运行爬虫程序
        
        Args:
            url: 目标URL
            output_file: 输出文件路径
            
        Returns:
            运行是否成功
        """
        start_time = time.time()
        logging.info("Starting JetBrains License Crawler")
        
        try:
            # 获取激活码
            licenses = self.fetch_licenses(url)
            
            if not licenses:
                logging.warning("No licenses found")
                return False
            
            # 保存激活码
            success = self.save_licenses(licenses, output_file)
            
            elapsed_time = time.time() - start_time
            logging.info(f"Crawler completed in {elapsed_time:.2f} seconds")
            
            return success
            
        except Exception as e:
            logging.error(f"Crawler failed: {e}")
            return False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="JetBrains License Auto Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python AutoJetBrainsLicense.py
  python AutoJetBrainsLicense.py --url https://example.com --output licenses.txt
  python AutoJetBrainsLicense.py --config custom_config.json --verbose
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        type=str,
        help='Target URL to crawl licenses from'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path for licenses'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--generate-config',
        action='store_true',
        help='Generate default configuration file and exit'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    try:
        args = parse_arguments()
        
        # 生成配置文件
        if args.generate_config:
            config = LicenseCrawlerConfig(args.config)
            config.save_config()
            print(f"Configuration file generated: {args.config}")
            return 0
        
        # 加载配置
        config = LicenseCrawlerConfig(args.config)
        
        # 设置日志级别
        if args.debug:
            config.config["log_level"] = "DEBUG"
        elif args.verbose:
            config.config["log_level"] = "INFO"
        
        # 创建爬虫实例并运行
        with JetBrainsLicenseCrawler(config) as crawler:
            success = crawler.run(args.url, args.output)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Program failed with error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
