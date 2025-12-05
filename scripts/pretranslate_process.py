import os
import json
import shutil
import argparse
import datetime

import import_db_json
import export_db_json


def values_to_keys():
    root_dir = input("export 文件夹: ") or "exports"
    output_dir = "./pretranslate_todo/full_out"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(".json"):
                continue

            data = {}
            with open(os.path.join(root, name), 'r', encoding='utf-8') as f:
                orig_data = json.load(f)

            for _, v in orig_data.items():
                data[v] = ""

            with open(os.path.join(output_dir, name), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print("save file", name)


def pretranslated_to_kv_files(
        root_dir: str,
        translated_dir: str,
        save_dir="pretranslate_todo/translated_out"
):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for root, dirs, files in os.walk(translated_dir):
        for name in files:
            if not name.endswith("_translated.json"):
                continue
            translated_file = os.path.join(root, name)
            print("\n!!! 当前处理文件绝对路径:", os.path.abspath(translated_file))  # 新增此行
            orig_file = os.path.join(root_dir, name[:-16] + ".json")
            save_file = os.path.join(save_dir, name[:-16] + ".json")

            with open(translated_file, 'r', encoding='utf-8') as f:
                translated_data = json.load(f)  # 日文: 原文

            with open(orig_file, 'r', encoding='utf-8') as f:
                orig_data = json.load(f)  # key: 日文

            for k, orig_jp in orig_data.items():
                orig_data[k] = translated_data.get(orig_jp, orig_jp)

            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(orig_data, f, ensure_ascii=False, indent=4)

            print("合并文件", name)
    print("合并完成，接下来请执行 import_db_json 将翻译文件导回")


def backup_temp_key_jp():
    """
    备份当前的 temp_key_jp 到 temp_key_jp_old
    """
    temp_key_jp_dir = "./pretranslate_todo/temp_key_jp"
    temp_key_jp_old_dir = "./pretranslate_todo/temp_key_jp_old"
    
    if not os.path.exists(temp_key_jp_dir):
        print("❌ 错误：temp_key_jp 目录不存在，请先运行数据更新操作")
        return False
    
    print("📁 开始备份当前 temp_key_jp 到 temp_key_jp_old...")
    
    # 如果旧备份存在，先删除
    if os.path.exists(temp_key_jp_old_dir):
        print("🗑️  删除旧的备份目录...")
        shutil.rmtree(temp_key_jp_old_dir)
    
    # 复制目录
    try:
        shutil.copytree(temp_key_jp_dir, temp_key_jp_old_dir)
        print("✅ 备份完成！")
        return True
    except Exception as e:
        print(f"❌ 备份失败：{e}")
        return False


def gen_todo(new_files_dir: str):
    """
    生成未翻译过的 jp: "" 文件
    """
    old_files_dir = "./data"
    temp_key_cn_dir = "./pretranslate_todo/temp_key_cn"
    temp_key_jp_dir = "./pretranslate_todo/temp_key_jp"
    temp_key_jp_old_dir = "./pretranslate_todo/temp_key_jp_old"  # 添加旧版本目录
    todo_out_dir = "./pretranslate_todo/todo"
    changed_out_dir = "./pretranslate_todo/todo/changed"  # 变化文件输出目录
    
    # 检查 temp_key_jp_old 目录是否存在
    if not os.path.exists(temp_key_jp_old_dir):
        print("⚠️  警告：temp_key_jp_old 目录不存在！")
        print("🔍 这意味着日文值变化检测功能将无法工作")
        print("📝 只能检测新增的键，无法检测已有键的日文值变化")
        print("💡 建议执行以下操作之一：")
        print("   1. 运行 'make backup' 或 'python scripts/pretranslate_process.py --backup' 来创建备份")
        print("   2. 如果这是首次运行，可以忽略此警告")
        
        user_choice = input("是否继续执行？(y/N): ").lower().strip()
        if user_choice not in ['y', 'yes']:
            print("❌ 操作已取消")
            return
        
        print("⚠️  继续执行，但日文值变化检测功能已禁用")
    
    # 创建日志文件
    log_file = f"./pretranslate_todo/jp_changes_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    changes_log = []
    changed_files = {}  # 存储每个文件的变化 {文件名: {(旧值, 新值): 旧翻译}}

    if not os.path.isdir(temp_key_cn_dir):
        os.makedirs(temp_key_cn_dir)
    if not os.path.isdir(temp_key_jp_dir):
        os.makedirs(temp_key_jp_dir)
    if not os.path.isdir(todo_out_dir):
        os.makedirs(todo_out_dir)
    if not os.path.isdir(changed_out_dir):
        os.makedirs(changed_out_dir)

    # 旧已翻译插件 json 转 key: cn
    for root, dirs, files in os.walk(old_files_dir):
        for file in files:
            if file.endswith(".json"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(temp_key_cn_dir, file)
                export_db_json.ex_main(input_path, output_path)

    # 新插件 json 转 key: jp
    for root, dirs, files in os.walk(new_files_dir):
        for file in files:
            if file.endswith(".json"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(temp_key_jp_dir, file)
                export_db_json.ex_main(input_path, output_path)

                # 特例处理：ProduceCardCustomize.json
                if file == "ProduceCardCustomize.json":
                    with open(input_path, 'r', encoding='utf-8') as f:
                        jp_data = json.load(f)

                    # 讀取原始 data 陣列，組合扁平化 key
                    with open(output_path, 'r', encoding='utf-8') as f:
                        out_data = json.load(f)

                    for entry in jp_data.get("data", []):
                        composite_key = f"{entry['id']}|{entry['customizeCount']}|description"
                        # 即使 description 是空字串也要寫入
                        out_data[composite_key] = entry.get("description", "")

                    # 覆寫回輸出檔案
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(out_data, f, ensure_ascii=False, indent=4)

                    print(f"特例處理完成: {output_path}")

    # 遍历新的 jp 文件
    for root, dirs, files in os.walk(temp_key_jp_dir):
        for file in files:
            jp_file = os.path.join(root, file)
            jp_old_file = os.path.join(temp_key_jp_old_dir, file)  # 旧版本日文文件
            cn_file = os.path.join(temp_key_cn_dir, file)
            out_data = {}

            with open(jp_file, 'r', encoding='utf-8') as f:
                jp_data = json.load(f)

            # 加载旧版本的日文数据
            jp_old_data = {}
            if os.path.exists(temp_key_jp_old_dir) and os.path.exists(jp_old_file):
                with open(jp_old_file, 'r', encoding='utf-8') as f:
                    jp_old_data = json.load(f)
            
            if not os.path.exists(cn_file):
                # 如果没有旧的翻译文件，所有日文都需要翻译
                for _, v in jp_data.items():
                    out_data[v] = ""
            else:
                with open(cn_file, 'r', encoding='utf-8') as f:
                    cn_data = json.load(f)
                for k, v in jp_data.items():
                    # 检查条件：
                    # 1. 键不存在于旧翻译中 (新增的键)
                    # 2. 键存在于旧翻译中，但日文值发生了变化 (值更新的键)
                    if k not in cn_data:
                        # 新增的键，直接添加
                        out_data[v] = ""
                    elif k in jp_old_data and jp_old_data[k] != v and k in cn_data:
                        # 键存在，日文值发生变化，且之前有翻译
                        change_info = f"文件: {file}\n键: {k}\n旧值: {jp_old_data[k]}\n新值: {v}\n原翻译: {cn_data[k]}\n{'='*50}"
                        changes_log.append(change_info)
                        # 记录到变化文件字典（去重相同的旧值->新值变化）
                        if file not in changed_files:
                            changed_files[file] = {}
                        change_key = (jp_old_data[k], v)
                        if change_key not in changed_files[file]:
                            changed_files[file][change_key] = cn_data[k]
                        print(f"检测到日文值变化: {file} - {k}")
                        print(f"  旧值: {jp_old_data[k]}")
                        print(f"  新值: {v}")
                        print(f"  原翻译: {cn_data[k]}")
                        out_data[v] = ""
            if out_data:
                todo_file = os.path.join(todo_out_dir, file)
                with open(todo_file, 'w', encoding='utf-8') as f:
                    json.dump(out_data, f, ensure_ascii=False, indent=4)
                print("TODO File", todo_file)
    
    # 保存变化的文件到 changed 目录（CSV格式）
    for file_name, changes in changed_files.items():
        changed_file_path = os.path.join(changed_out_dir, file_name.replace('.json', '.csv'))
        with open(changed_file_path, 'w', encoding='utf-8', newline='') as f:
            # 手动写入CSV格式，完全保持原样
            f.write('旧值,新值,旧翻译,新翻译\n')
            for (old_value, new_value), old_translation in changes.items():
                # 直接拼接，完全按原样保存
                line = f'{old_value},{new_value},{old_translation},\n'
                f.write(line)
        print(f"变化文件已保存: {changed_file_path} (包含 {len(changes)} 个唯一变化)")
    
    # 保存变化日志
    if changes_log:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"日文值变化检测报告\n")
            f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"检测到 {len(changes_log)} 处变化\n")
            f.write("="*80 + "\n\n")
            f.write("\n\n".join(changes_log))
        print(f"\n变化日志已保存到: {log_file}")
        print(f"共检测到 {len(changes_log)} 处日文值变化")
        print(f"变化文件已保存到: {changed_out_dir}")
    else:
        print("\n未检测到日文值变化")
    
    # 添加最终状态报告
    if not os.path.exists(temp_key_jp_old_dir):
        print("\n📊 执行状态报告：")
        print("✅ 新增键检测：已执行")
        print("❌ 日文值变化检测：已跳过（缺少备份目录）")
        print("💡 下次运行前建议先执行备份操作")


def merge_todo():
    new_files_dir = "./pretranslate_todo/todo/new"  # 只有新的 jp: cn
    old_trans_dir = "./pretranslate_todo/temp_key_cn"  # 旧版 key: cn
    new_key_jp_dir = "./pretranslate_todo/temp_key_jp"  # 新版 key: jp
    output_dir = "./pretranslate_todo/merged"  # 新的 key: cn

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # 首先将新的 key: jp 复制到输出文件夹
    for root, dirs, files in os.walk(new_key_jp_dir):
        for file in files:
            if file.endswith(".json"):
                shutil.copyfile(os.path.join(root, file), os.path.join(output_dir, file))

    # 合并旧翻译
    for root, dirs, files in os.walk(old_trans_dir):
        for file in files:
            if file.endswith(".json"):
                old_key_cn_file = os.path.join(root, file)  # 旧版 key: cn
                new_key_jp_file = os.path.join(output_dir, file)  # 目前 output_dir 是新版 key: jp

                with open(old_key_cn_file, 'r', encoding='utf-8') as f:
                    old_key_cn_data: dict = json.load(f)
                if os.path.exists(new_key_jp_file):
                    with open(new_key_jp_file, 'r', encoding='utf-8') as f:
                        new_key_jp_data = json.load(f)
                else:
                    new_key_jp_data = {}

                for k, v in old_key_cn_data.items():
                    new_key_jp_data[k] = v

                with open(new_key_jp_file, 'w', encoding='utf-8') as f:
                    json.dump(new_key_jp_data, f, ensure_ascii=False, indent=4)

    pretranslated_to_kv_files(output_dir, new_files_dir, output_dir)

    if input("继续执行 import_db_json，请输入 1: ") == "1":
        import_db_json.main("./gakumasu-diff/json", output_dir, "data")
        print("文件已输出到 data")


def apply_changed_translations():
    """
    应用 changed 文件夹中的新翻译到 temp_key_cn 和 jp_cn 文件夹
    """
    changed_dir = "./pretranslate_todo/todo/changed"
    temp_key_cn_dir = "./pretranslate_todo/temp_key_cn"
    temp_key_jp_dir = "./pretranslate_todo/temp_key_jp"
    jp_cn_dir = "./pretranslate_todo/jp_cn"
    
    if not os.path.exists(changed_dir):
        print("❌ 错误：changed 文件夹不存在")
        return False
    
    if not os.path.exists(temp_key_jp_dir):
        print("❌ 错误：temp_key_jp 文件夹不存在")
        return False
    
    # 确保目标文件夹存在
    if not os.path.exists(temp_key_cn_dir):
        os.makedirs(temp_key_cn_dir)
    if not os.path.exists(jp_cn_dir):
        os.makedirs(jp_cn_dir)
    
    print("🔄 开始处理 changed 文件夹中的翻译更新...")
    
    updated_count = 0
    processed_files = 0
    
    # 遍历 changed 文件夹中的所有 CSV 文件
    for filename in os.listdir(changed_dir):
        if not filename.endswith('.csv'):
            continue
            
        csv_file_path = os.path.join(changed_dir, filename)
        json_filename = filename.replace('.csv', '.json')
        
        print(f"\n📄 处理文件: {filename}")
        
        # 读取对应的 temp_key_jp 文件
        temp_key_jp_file = os.path.join(temp_key_jp_dir, json_filename)
        if not os.path.exists(temp_key_jp_file):
            print(f"⚠️  警告：找不到对应的 temp_key_jp 文件: {json_filename}")
            continue
        
        with open(temp_key_jp_file, 'r', encoding='utf-8') as f:
            temp_key_jp_data = json.load(f)
        
        # 读取或创建对应的 temp_key_cn 文件
        temp_key_cn_file = os.path.join(temp_key_cn_dir, json_filename)
        if os.path.exists(temp_key_cn_file):
            with open(temp_key_cn_file, 'r', encoding='utf-8') as f:
                temp_key_cn_data = json.load(f)
        else:
            temp_key_cn_data = {}
        
        # 读取或创建对应的 jp_cn 文件
        jp_cn_file = os.path.join(jp_cn_dir, json_filename)
        if os.path.exists(jp_cn_file):
            with open(jp_cn_file, 'r', encoding='utf-8') as f:
                jp_cn_data = json.load(f)
        else:
            jp_cn_data = {}
        
        # 处理 CSV 文件
        file_updated_count = 0
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                # 手动解析CSV，避免复杂的转义问题
                lines = f.readlines()
                if len(lines) <= 1:  # 只有标题行或空文件
                    continue
                
                for line_num, line in enumerate(lines[1:], 2):  # 跳过标题行
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析CSV行：旧值,新值,旧翻译,新翻译
                    parts = line.split(',')
                    if len(parts) < 4:
                        print(f"⚠️  第{line_num}行格式错误，跳过: {line}")
                        continue
                    
                    # 处理可能包含逗号的字段（简单处理）
                    if len(parts) > 4:
                        # 假设只有最后一个字段（新翻译）可能包含逗号
                        old_value = parts[0]
                        new_value = parts[1]
                        old_translation = parts[2]
                        new_translation = ','.join(parts[3:])
                    else:
                        old_value, new_value, old_translation, new_translation = parts
                    
                    # 不做任何转义处理，完全按原样使用
                    
                    # 如果新翻译为空，跳过
                    if not new_translation.strip():
                        continue
                    
                    # 读取对应的旧版本 temp_key_jp 文件来精确匹配变化的键
                    temp_key_jp_old_file = os.path.join("./pretranslate_todo/temp_key_jp_old", json_filename)
                    if not os.path.exists(temp_key_jp_old_file):
                        print(f"⚠️  警告：找不到旧版本文件，无法精确匹配变化: {json_filename}")
                        continue
                    
                    with open(temp_key_jp_old_file, 'r', encoding='utf-8') as f:
                        temp_key_jp_old_data = json.load(f)
                    
                    # 找到确实发生变化的键：旧值 -> 新值
                    matching_keys = []
                    for key, old_jp_value in temp_key_jp_old_data.items():
                        if (old_jp_value == old_value and 
                            key in temp_key_jp_data and 
                            temp_key_jp_data[key] == new_value):
                            matching_keys.append(key)
                    
                    if not matching_keys:
                        print(f"⚠️  找不到从'{old_value[:20]}...'变为'{new_value[:20]}...'的键")
                        continue
                    
                    # 更新所有匹配的键
                    for key in matching_keys:
                        # 更新 temp_key_cn
                        temp_key_cn_data[key] = new_translation
                        file_updated_count += 1
                    
                    # 更新 jp_cn（只在键不存在时添加新的映射）
                    if new_value not in jp_cn_data:
                        jp_cn_data[new_value] = new_translation
                    elif jp_cn_data[new_value] != new_translation:
                        # 如果键存在但值不同，更新为新翻译
                        jp_cn_data[new_value] = new_translation
                    
                    print(f"✅ 更新翻译 ({len(matching_keys)}个键): '{old_value[:20]}...' -> '{new_value[:20]}...' = '{new_translation[:20]}...'")
        
        except Exception as e:
            print(f"❌ 处理 CSV 文件时出错: {e}")
            continue
        
        # 保存更新后的文件
        if file_updated_count > 0:
            with open(temp_key_cn_file, 'w', encoding='utf-8') as f:
                json.dump(temp_key_cn_data, f, ensure_ascii=False, indent=2)
            
            with open(jp_cn_file, 'w', encoding='utf-8') as f:
                json.dump(jp_cn_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 已保存 {file_updated_count} 个翻译更新到 {json_filename}")
            updated_count += file_updated_count
            processed_files += 1
        else:
            print(f"ℹ️  {json_filename} 没有需要更新的翻译")
    
    print(f"\n🎉 处理完成！")
    print(f"📊 统计信息：")
    print(f"   - 处理的文件数: {processed_files}")
    print(f"   - 更新的翻译数: {updated_count}")
    
    if updated_count > 0:
        print(f"\n💡 提示：翻译已更新到以下文件夹：")
        print(f"   - temp_key_cn: {temp_key_cn_dir}")
        print(f"   - jp_cn: {jp_cn_dir}")
        print(f"   你可以继续执行后续的合并流程")
    
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gen_todo', action='store_true')
    parser.add_argument('--merge', action='store_true')
    parser.add_argument('--backup', action='store_true', help='备份当前的 temp_key_jp')
    parser.add_argument('--apply_changed', action='store_true', help='应用 changed 文件夹中的新翻译')
    args = parser.parse_args()

    if args.backup:
        backup_temp_key_jp()
        return

    if args.apply_changed:
        apply_changed_translations()
        return

    if (not args.gen_todo) and (not args.merge):
        do_idx = input("[1] 全部导出转为待翻译文件\n"
                       "[2] 对比更新病生成 todo 文件\n"
                       "[3] 翻译文件(jp: cn)转回 key-value json\n"
                       "[4] 将翻译后的 todo 文件合并回插件 json\n"
                       "[5] 备份当前 temp_key_jp\n"
                       "[6] 应用 changed 文件夹中的新翻译\n"
                       "请选择操作: ")
    elif args.gen_todo:
        gen_todo("gakumasu-diff/json")
        return
    elif args.merge:
        do_idx = "4"
    else:
        raise RuntimeError("Invalid Arguments.")

    if do_idx == "1":
        values_to_keys()

    elif do_idx == "2":
        gen_todo(input("新 gakumasu_diff_to_json 文件夹: ") or "gakumasu-diff/json")

    elif do_idx == "3":
        pretranslated_to_kv_files(
            root_dir=input("export 文件夹: ") or "exports",
            translated_dir=input("预翻译完成文件夹: ")
        )

    elif do_idx == "4":
        merge_todo()

    elif do_idx == "5":
        backup_temp_key_jp()

    elif do_idx == "6":
        apply_changed_translations()


if __name__ == '__main__':
    main()
