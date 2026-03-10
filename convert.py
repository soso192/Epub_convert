#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB 繁体转简体转换器
将 EPUB 电子书文件中的繁体中文转换为简体中文
"""

import os
import sys
import shutil
import tempfile
import zipfile
from pathlib import Path

try:
    import opencc
except ImportError:
    print("请先安装 opencc-python: pip install opencc-python-reimplemented")
    sys.exit(1)

try:
    from ebooklib import epub
except ImportError:
    print("请先安装 ebooklib: pip install EbookLib")
    sys.exit(1)

from ebooklib import epub


class EpubConverter:
    def __init__(self):
        # 创建 OpenCC 转换器（台湾繁体转大陆简体）
        self.converter = opencc.OpenCC('tw2s')  # 台湾繁体转简体
        # 也可以使用 't2s'（通用繁体转简体）
        
    def convert_text(self, text):
        """将文本中的繁体字转换为简体字"""
        if not text:
            return text
        return self.converter.convert(text)
    
    def process_html_content(self, content):
        """处理 HTML 内容中的文本节点"""
        from html.parser import HTMLParser
        
        class TextConverter(HTMLParser):
            def __init__(self, converter):
                super().__init__()
                self.converter = converter
                self.result = []
                self.in_script_or_style = False
                
            def handle_starttag(self, tag, attrs):
                # 跳过 script 和 style 标签内的内容
                if tag.lower() in ['script', 'style']:
                    self.in_script_or_style = True
                    
                # 重建开始标签
                attrs_str = ''
                for attr, value in attrs:
                    if value is not None:
                        # 转换属性值中的文本（如 title, alt 等）
                        converted_value = self.converter.convert(value)
                        # 处理引号转义
                        if '"' in converted_value:
                            converted_value = converted_value.replace('"', '&quot;')
                        attrs_str += f' {attr}="{converted_value}"'
                    else:
                        attrs_str += f' {attr}'
                self.result.append(f'<{tag}{attrs_str}>')
                
            def handle_endtag(self, tag):
                if tag.lower() in ['script', 'style']:
                    self.in_script_or_style = False
                self.result.append(f'</{tag}>')
                
            def handle_data(self, data):
                if self.in_script_or_style:
                    # 不转换 script/style 内的代码
                    self.result.append(data)
                else:
                    # 转换文本内容
                    converted = self.converter.convert(data)
                    self.result.append(converted)
                    
            def handle_entityref(self, name):
                self.result.append(f'&{name};')
                
            def handle_charref(self, name):
                self.result.append(f'&#{name};')
                
            def get_result(self):
                return ''.join(self.result)
        
        try:
            parser = TextConverter(self.converter)
            parser.feed(content)
            return parser.get_result()
        except Exception as e:
            print(f"HTML 解析失败，使用纯文本转换: {e}")
            # 备用方案：直接转换整个文本
            return self.converter.convert(content)
    
    def convert_epub(self, input_path, output_path=None):
        """
        转换 EPUB 文件
        
        Args:
            input_path: 输入的 EPUB 文件路径
            output_path: 输出的 EPUB 文件路径（默认为原文件名_add_simplified.epub）
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"找不到文件: {input_path}")
        
        if input_path.suffix.lower() != '.epub':
            raise ValueError("只支持 EPUB 格式的文件")
        
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_simplified.epub"
        else:
            output_path = Path(output_path)
        
        print(f"正在处理: {input_path}")
        print(f"输出文件: {output_path}")
        
        # 读取原 EPUB
        book = epub.read_epub(str(input_path))
        
        # 处理所有文档项
        converted_count = 0
        for item in book.get_items():
            if isinstance(item, epub.EpubHtml):
                # 获取原始内容
                try:
                    original_content = item.get_content().decode('utf-8', errors='ignore')
                    
                    # 转换内容
                    converted_content = self.process_html_content(original_content)
                    
                    # 更新内容
                    item.set_content(converted_content.encode('utf-8'))
                    converted_count += 1
                    
                    # 同时转换标题
                    if hasattr(item, 'title') and item.title:
                        item.title = self.convert_text(item.title)
                except Exception as e:
                    print(f"  警告: 处理 {item.get_name()} 时出错: {e}")
                    continue
                    
            elif isinstance(item, epub.EpubNav):
                # 处理导航文件
                try:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    converted = self.process_html_content(content)
                    item.set_content(converted.encode('utf-8'))
                except Exception as e:
                    print(f"  警告: 处理导航文件时出错: {e}")
                
            elif isinstance(item, epub.EpubNcx):
                # 处理 NCX 目录文件
                try:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    converted = self.process_html_content(content)
                    item.set_content(converted.encode('utf-8'))
                except Exception as e:
                    print(f"  警告: 处理 NCX 文件时出错: {e}")
        
        # 转换书籍元数据（修复元组不可变问题）
        try:
            if hasattr(book, 'title') and book.title:
                book.title = self.convert_text(book.title)
        except Exception as e:
            print(f"  警告: 转换标题时出错: {e}")
        
        # 保存转换后的 EPUB
        try:
            epub.write_epub(str(output_path), book)
            print(f"✓ 转换完成！共处理 {converted_count} 个 HTML 文件")
            print(f"✓ 已保存至: {output_path}")
        except Exception as e:
            print(f"保存文件失败: {e}")
            raise
        
        return output_path


def batch_convert(directory):
    """批量转换目录中的所有 EPUB 文件"""
    directory = Path(directory)
    epub_files = list(directory.glob("*.epub"))
    
    if not epub_files:
        print(f"在 {directory} 中未找到 EPUB 文件")
        return
    
    print(f"找到 {len(epub_files)} 个 EPUB 文件")
    
    converter = EpubConverter()
    for epub_file in epub_files:
        try:
            # 跳过已转换的文件
            if "_simplified" in epub_file.stem:
                print(f"跳过已转换文件: {epub_file.name}")
                continue
                
            converter.convert_epub(epub_file)
            print("-" * 50)
        except Exception as e:
            print(f"转换失败 {epub_file.name}: {e}")
            print("-" * 50)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='将 EPUB 文件中的繁体中文转换为简体中文',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python epub_converter.py book.epub                    # 转换单个文件
  python epub_converter.py book.epub -o output.epub     # 指定输出文件名
  python epub_converter.py -d ./books/                  # 批量转换目录中的所有 EPUB
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入的 EPUB 文件路径')
    parser.add_argument('-o', '--output', help='输出的 EPUB 文件路径')
    parser.add_argument('-d', '--directory', help='批量转换目录中的所有 EPUB 文件')
    
    args = parser.parse_args()
    
    if args.directory:
        batch_convert(args.directory)
    elif args.input:
        converter = EpubConverter()
        converter.convert_epub(args.input, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()