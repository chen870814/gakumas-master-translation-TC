update:
	cd gakumasu-diff/orig && git fetch && git checkout origin/main
	python scripts/gakumasu_diff_to_json.py

backup:
	python scripts/pretranslate_process.py --backup

gentodo:
	python scripts/pretranslate_process.py --gen_todo

merge:
	python scripts/incremental_merge.py

jpcn:
	python scripts/jp_cn.py

rename:
	python scripts/rename.py

tran:
	python scripts/full_trans.py