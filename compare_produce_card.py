import json
import csv

def remove_plus_variants(differences):
    """
    过滤掉只有"+"符号差异的变体，只保留基础版本
    """
    # 创建一个字典来存储基础版本
    base_versions = {}
    
    for diff in differences:
        key = diff['key']
        # 移除所有的"+"符号来获取基础键名
        base_key = key.rstrip('+')
        
        # 如果这是基础版本（没有"+"符号），直接保存
        if key == base_key:
            base_versions[base_key] = diff
        # 如果基础版本还不存在，保存这个条目
        elif base_key not in base_versions:
            # 创建一个基础版本的条目
            base_versions[base_key] = {
                'key': base_key,
                'file1_value': diff['file1_value'].rstrip('+'),
                'file2_value': diff['file2_value'].rstrip('+')
            }
    
    return list(base_versions.values())

def compare_produce_card_files():
    # 读取两个JSON文件
    with open('ProduceCard.json', 'r', encoding='utf-8') as f1:
        file1_data = json.load(f1)
    
    with open('pretranslate_todo/jp_cn/ProduceCard.json', 'r', encoding='utf-8') as f2:
        file2_data = json.load(f2)
    
    # 找出相同键但不同值的情况
    differences = []
    
    for key in file1_data:
        if key in file2_data:
            if file1_data[key] != file2_data[key]:
                differences.append({
                    'key': key,
                    'file1_value': file1_data[key],
                    'file2_value': file2_data[key]
                })
    
    print(f"原始发现 {len(differences)} 个差异")
    
    # 过滤掉"+"变体，只保留基础版本
    filtered_differences = remove_plus_variants(differences)
    
    print(f"过滤后剩余 {len(filtered_differences)} 个基础版本差异")
    
    # 将过滤后的差异写入CSV文件
    with open('produce_card_differences_filtered.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['key', 'file1_value', 'file2_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for diff in filtered_differences:
            writer.writerow(diff)
    
    print(f"已保存到 produce_card_differences_filtered.csv")

if __name__ == "__main__":
    compare_produce_card_files()