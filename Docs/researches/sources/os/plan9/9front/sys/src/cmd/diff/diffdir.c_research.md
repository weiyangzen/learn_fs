# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffdir.c

Plan 9 `diff` directory dispatcher. It scans directories, sorts child names, reports entries present only on one side, and routes matching names into recursive directory comparison or regular file comparison.

Key behavior:
- `scandir` opens a directory, reads all `Dir` entries with `dirreadall`, copies names into a null-terminated `char **`, and sorts with `qsort`.
- `diffdir` walks the two sorted name lists, skips `.` and `..`, emits `Only in ...` lines for unmatched entries in normal and `-n` modes, and calls `diff` for common names.
- `diff` stats both inputs through `statfile`, handles stdin/special-file temporary conversion indirectly, compares directories recursively only when `rflag` or top-level, compares regular files with `diffreg`, and handles file-vs-directory by comparing the regular file to a same-basename child path under the directory.

Notable dependencies:
- Shared globals and helpers from `diff.h`/`util.c`: `mode`, `rflag`, `mflag`, `mkpathname`, `statfile`, `emalloc`, `erealloc`.
- Plan 9 `Dir` metadata and `QTDIR`/type checks.

Research notes:
- `scandir` treats an unopenable directory as empty after printing an error, allowing comparison to continue.
- Path building is bounded by `MAXPATHLEN`, with too-long paths fataling in `mkpathname`.
- Directory entries are freed after traversal; `statfile` results are also freed before return.
