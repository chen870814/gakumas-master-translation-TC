update:
	@echo "备份当前 temp_key_jp 到 temp_key_jp_old..."
	@if [ -d "pretranslate_todo/temp_key_jp" ]; then \
		rm -rf pretranslate_todo/temp_key_jp_old; \
		cp -r pretranslate_todo/temp_key_jp pretranslate_todo/temp_key_jp_old; \
		echo "备份完成"; \
	else \
		echo "temp_key_jp 目录不存在，跳过备份"; \
	fi
	cd gakumasu-diff/orig && git fetch && git checkout origin/main
	python scripts/gakumasu_diff_to_json.py

gen-todo:
	python scripts/pretranslate_process.py --gen_todo

merge:
	python scripts/pretranslate_process.py --merge