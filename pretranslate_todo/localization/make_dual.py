import json
import os

base_dir = r'D:\Documents\GitHub\gakumas-master-translation-TC\pretranslate_todo\localization'
full_path = os.path.join(base_dir, 'localization_full.json')
local_path = os.path.join(base_dir, 'localization.json')
output_path = os.path.join(base_dir, 'translated_dual.json')

with open(full_path, 'r', encoding='utf-8') as f:
    full_data = json.load(f)
with open(local_path, 'r', encoding='utf-8') as f:
    local_data = json.load(f)

result = {}
for key in full_data.keys():  # 按full的顺序
    if key in local_data:
        result[key] = {
            "japanese": full_data[key],
            "chinese": local_data[key]
        }
    else:
        result[key] = {
            "japanese": full_data[key],
            "chinese": ""
        }

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("已生成 translated_dual.json")