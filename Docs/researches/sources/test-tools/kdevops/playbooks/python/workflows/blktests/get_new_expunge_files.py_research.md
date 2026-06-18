# sources/test-tools/kdevops/playbooks/python/workflows/blktests/get_new_expunge_files.py

Purpose: lists expunge files that are new relative to the current git tree.

Important APIs/types/functions: `main` parses `expunge_dir`, walks files, and calls `lib.git.is_new_file(f)` to detect untracked/new files. Outputs a shortened path when it contains `../`.

Control flow: recursively scan the expunge directory, skip non-files, query git status for each file, and print files not yet committed.

State/persistence behavior: read-only; it inspects working tree state without modifying files.

Dependencies/integration: supports blktests expunge maintenance by identifying newly generated failure files that need review/commit.

Risks/test signals: depends on local `lib.git` helper and current working directory; unused `pwd` and imports indicate minimal cleanup. Test signals are correct listing of untracked expunge files and no output for already tracked files.
