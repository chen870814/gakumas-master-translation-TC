update:
	@echo "备份当前 temp_key_jp 到 temp_key_jp_old..."
	@if exist "pretranslate_todo\temp_key_jp" ( \
		if exist "pretranslate_todo\temp_key_jp_old" rmdir /s /q "pretranslate_todo\temp_key_jp_old" & \
		xcopy "pretranslate_todo\temp_key_jp" "pretranslate_todo\temp_key_jp_old" /e /i /q & \
		echo "备份完成" \
	) else ( \
		echo "temp_key_jp 目录不存在，跳过备份" \
	)
	cd gakumasu-diff\orig && git fetch && git checkout origin/main
	python scripts/gakumasu_diff_to_json.py

gen-todo:
	python scripts/pretranslate_process.py --gen_todo

merge:
	python scripts/pretranslate_process.py --merge