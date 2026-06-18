# sources/test-tools/lcov/bin/copy_dates.sh

Purpose: copies modification timestamps from a source tree to a target tree, preferring the latest git commit time for clean tracked files. It is used to make distribution trees carry stable source-history dates.

Important APIs/types/functions: shell argument validation, `.git` detection, optional verbose mode through `V`, `find`, `touch -r`, `git diff --quiet`, `git diff --cached --quiet`, `git log --pretty=format:%cd --date=iso`, and `touch --date`.

Control flow: the script requires `SOURCE` and `TARGET`, records whether `SOURCE/.git` exists, changes into `SOURCE`, and walks every file under `find * -type f`. Missing target counterparts are skipped. For every matching file it first copies the source file mtime. If the source is a git repository and the file has no unstaged or staged modifications, it replaces that mtime with the most recent commit date for that file.

State/persistence behavior: only target file mtimes are mutated. Source files and git state are read-only. Files without a target counterpart or without a commit timestamp are left at their copied source mtime.

Dependencies/integration: called by the lcov Makefile during tarball creation and release preparation. It supports reproducible or history-aligned release artifacts before `fix.pl` adjusts embedded dates.

Risks/test signals: `find *` skips dotfiles at the source root and can behave poorly with newlines in filenames. Git errors are not fatal inside the loop except through command exit behavior, and untracked files get source mtimes rather than commit dates. Signals are target mtimes matching clean git commit dates for tracked files and source mtimes for dirty or non-git files.
