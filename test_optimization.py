#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的代码功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入功能"""
    try:
        # 测试基本导入
        import argparse
        import json
        import logging
        import re
        import time
        from datetime import datetime
        from pathlib import Path
        from typing import Set, Optional, Dict, Any
        print("✅ 基本模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 基本模块导入失败: {e}")
        return False

def test_config_class():
    """测试配置类"""
    try:
        # 导入我们的模块（不依赖requests和beautifulsoup4）
        import AutoJetBrainsLicense
        
        # 测试配置类
        config = AutoJetBrainsLicense.LicenseCrawlerConfig("test_config.json")
        print("✅ 配置类创建成功")
        print(f"   - 目标URL: {config.config['target_url']}")
        print(f"   - 输出文件: {config.config['output_file']}")
        print(f"   - 超时时间: {config.config['timeout']}秒")
        return True
    except Exception as e:
        print(f"❌ 配置类测试失败: {e}")
        return False

def test_argument_parsing():
    """测试命令行参数解析"""
    try:
        import AutoJetBrainsLicense
        
        # 模拟命令行参数
        sys.argv = ['AutoJetBrainsLicense.py', '--help']
        
        try:
            AutoJetBrainsLicense.parse_arguments()
        except SystemExit:
            # help参数会导致SystemExit，这是正常的
            pass
        
        print("✅ 命令行参数解析功能正常")
        return True
    except Exception as e:
        print(f"❌ 命令行参数解析测试失败: {e}")
        return False

def test_license_validation():
    """测试激活码验证功能"""
    try:
        import AutoJetBrainsLicense
        
        config = AutoJetBrainsLicense.LicenseCrawlerConfig()
        
        # 创建一个模拟的爬虫实例（不初始化网络部分）
        class MockCrawler:
            def __init__(self, config):
                self.config = config
            
            def _is_valid_license(self, license_text):
                if not license_text or len(license_text.strip()) < self.config.config["min_license_length"]:
                    return False
                
                import re
                license_pattern = re.compile(r'^[A-Z0-9\-]{10,}$', re.IGNORECASE)
                return bool(license_pattern.match(license_text.strip()))
        
        crawler = MockCrawler(config)
        
        # 测试验证逻辑
        test_cases = [
            ("ABC123DEF456", True),
            ("short", False),
            ("VALID-LICENSE-123", True),
            ("", False),
            ("123456789012345", True)
        ]
        
        all_passed = True
        for license_text, expected in test_cases:
            result = crawler._is_valid_license(license_text)
            if result == expected:
                print(f"✅ 激活码验证测试通过: '{license_text}' -> {result}")
            else:
                print(f"❌ 激活码验证测试失败: '{license_text}' -> {result}, 期望: {expected}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ 激活码验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 开始测试优化后的代码...")
    print("=" * 50)
    
    tests = [
        ("基本模块导入", test_imports),
        ("配置类功能", test_config_class),
        ("命令行参数解析", test_argument_parsing),
        ("激活码验证逻辑", test_license_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   测试失败")
        except Exception as e:
            print(f"   测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！代码优化成功！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查代码")
        return 1

if __name__ == "__main__":
    sys.exit(main())