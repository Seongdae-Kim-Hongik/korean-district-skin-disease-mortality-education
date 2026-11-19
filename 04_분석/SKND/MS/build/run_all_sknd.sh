#!/bin/bash
# run_all_sknd.sh — SKND manuscript build (numbers → refs → figures → manuscript → supporting information → cover letter → checks)
set -e; cd "$(dirname "$0")"
python3 numbers_sknd.py >/dev/null
python3 build_refs_sknd.py >/dev/null
python3 figs_sknd.py
python3 build_jddg_sknd.py
python3 esm_sknd.py
python3 cover_jddg_sknd.py "$@"
python3 sanitize_docx.py --no-anon ../out/Manuscript_JDDG_SKND.docx ../out/Supporting_Information_JDDG_SKND.docx ../out/Cover_Letter_JDDG_SKND.docx ../out/STROBE_Checklist_JDDG_SKND.docx
python3 check_jddg_sknd.py
