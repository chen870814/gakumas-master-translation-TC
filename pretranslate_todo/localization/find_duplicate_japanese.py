#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找相同 japanese 键值对但 chinese 不同的情况
"""

import json
from collections import defaultdict

def find_duplicate_japanese(json_file_path):
    """
    查找相同日文但中文不同的条目
    
    Args:
        json_file_path: JSON文件路径
    
    Returns:
        dict: 包含重复日文的字典，key为日文，value为包含该日文的所有条目
    """
    # 读取JSON文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"错误：JSON文件格式错误 - {e}")
        return {}
    
    # 用于存储日文到条目的映射
    japanese_to_entries = defaultdict(list)
    
    # 遍历所有条目
    for key, value in data.items():
        if isinstance(value, dict) and 'japanese' in value and 'chinese' in value:
            japanese_text = value['japanese']
            chinese_text = value['chinese']
            
            # 将条目添加到对应的日文组
            japanese_to_entries[japanese_text].append({
                'key': key,
                'japanese': japanese_text,
                'chinese': chinese_text
            })
    
    # 找出有多个不同中文翻译的日文条目
    duplicates = {}
    for japanese_text, entries in japanese_to_entries.items():
        if len(entries) > 1:
            # 检查是否有不同的中文翻译
            chinese_texts = set(entry['chinese'] for entry in entries)
            if len(chinese_texts) > 1:
                duplicates[japanese_text] = entries
    
    return duplicates

def print_results(duplicates):
    """
    打印结果
    
    Args:
        duplicates: 重复的日文条目字典
    """
    if not duplicates:
        print("未找到相同日文但中文不同的条目。")
        return
    
    print(f"找到 {len(duplicates)} 个相同日文但中文不同的情况：")
    print("=" * 80)
    
    for i, (japanese_text, entries) in enumerate(duplicates.items(), 1):
        print(f"\n{i}. 日文：{japanese_text}")
        print("-" * 60)
        
        for entry in entries:
            print(f'"{entry["key"]}": {{')
            print(f'    "japanese": "{entry["japanese"]}",')
            print(f'    "chinese": "{entry["chinese"]}"')
            print('},')
        
        # 显示所有不同的中文翻译
        chinese_texts = list(set(entry['chinese'] for entry in entries))
        print(f"\n不同的中文翻译（{len(chinese_texts)}个）:")
        for j, chinese in enumerate(chinese_texts, 1):
            print(f"  {j}. {chinese}")

def save_results_to_file(duplicates, output_file):
    """
    将结果保存到文件
    
    Args:
        duplicates: 重复的日文条目字典
        output_file: 输出文件路径
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("相同日文但中文不同的翻译条目\n")
            f.write("=" * 80 + "\n")
            f.write(f"总共找到 {len(duplicates)} 个重复项\n\n")
            
            for i, (japanese_text, entries) in enumerate(duplicates.items(), 1):
                f.write(f"{i}. 日文：{japanese_text}\n")
                f.write("-" * 60 + "\n")
                
                for entry in entries:
                    f.write(f'"{entry["key"]}": {{\n')
                    f.write(f'    "japanese": "{entry["japanese"]}",\n')
                    f.write(f'    "chinese": "{entry["chinese"]}"\n')
                    f.write('},\n')
                
                # 显示所有不同的中文翻译
                chinese_texts = list(set(entry['chinese'] for entry in entries))
                f.write(f"\n不同的中文翻译（{len(chinese_texts)}个）:\n")
                for j, chinese in enumerate(chinese_texts, 1):
                    f.write(f"  {j}. {chinese}\n")
                f.write("\n" + "="*80 + "\n\n")
        
        print(f"\n结果已保存到文件：{output_file}")
    except Exception as e:
        print(f"保存文件时出错：{e}")

def main():
    # JSON文件路径
    json_file = "translated_dual.json"
    output_file = "duplicate_japanese_analysis.txt"
    
    print("正在分析JSON文件...")
    duplicates = find_duplicate_japanese(json_file)
    
    # 打印结果到控制台
    print_results(duplicates)
    
    # 保存结果到文件
    save_results_to_file(duplicates, output_file)
    
    # 统计信息
    if duplicates:
        total_entries = sum(len(entries) for entries in duplicates.values())
        print(f"\n统计信息：")
        print(f"- 重复的日文条目数：{len(duplicates)}")
        print(f"- 涉及的总条目数：{total_entries}")
        
        # 找出重复最多的日文
        max_duplicates = max(len(entries) for entries in duplicates.values())
        most_duplicated = [jp for jp, entries in duplicates.items() if len(entries) == max_duplicates]
        print(f"- 重复次数最多的日文（{max_duplicates}次）：{most_duplicated[0] if most_duplicated else 'N/A'}")

if __name__ == "__main__":
    main()