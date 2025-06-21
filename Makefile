update:
	cd gakumasu-diff/orig && git fetch && git checkout origin/main
	python scripts/gakumasu_diff_to_json.py

backup:
	python scripts/pretranslate_process.py --backup

gen-todo:
	python scripts/pretranslate_process.py --gen_todo

apply-changed:
	python scripts/pretranslate_process.py --apply_changed

merge:
	python scripts/pretranslate_process.py --merge