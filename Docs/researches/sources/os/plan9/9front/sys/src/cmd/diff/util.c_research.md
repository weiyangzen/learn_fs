# File Research: sources/os/plan9/9front/sys/src/cmd/diff/util.c

Shared utility and global-state file for the Plan 9 `diff` command.

Key behavior:
- Defines global `stdout`, mode flags, recursion/multiple-file flags, and `anychange`.
- Provides fatal allocation wrappers `emalloc` and `erealloc`.
- `mkpathname` joins directory and child names with length enforcement.
- `mktmpfile` copies stdin or special-file contents to an ORCLOSE temporary file for stable diffing.
- `statfile` returns regular files/directories directly, maps `-` to stdin temp storage, and copies non-regular/non-directory readable files to a temp file.

Notable dependencies:
- Plan 9 temp naming via `mktemp`.
- Plan 9 `Dir` metadata and `ORCLOSE`.

Research notes:
- `mktmpfile` intentionally leaks the created fd so the temporary remains for the program’s lifetime and is removed at exit.
- Only two temp paths are statically defined, matching the two-input model.
