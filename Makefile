update:
	cd gakumasu-diff/orig && git fetch && git checkout origin/main
	python scripts/gakumasu_diff_to_json.py

backup:
	python scripts/pretranslate_process.py --backup

gen-todo:
	python scripts/pretranslate_process.py --gen_todo

merge:
	python scripts/incremental_merge.py