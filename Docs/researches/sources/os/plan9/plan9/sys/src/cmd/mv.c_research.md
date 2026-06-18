# File Research: sources/os/plan9/plan9/sys/src/cmd/mv.c

Implements Plan 9 `mv`.

Behavior:
- Supports `mv fromfile tofile` and `mv fromfile ... todir`.
- Cleans names before processing.
- If moving a single directory into an existing directory, treats it as rename of directory target.
- Same-directory moves attempt `dirwstat()` rename after removing any existing target.
- Cross-directory/file-server moves fall back to copy then remove for non-directories.

Key functions:
- `mv()` stats source and calls `mv1()`.
- `mv1()` resolves destination path, detects same file/dir, renames or copies, preserves mode and mtime where possible.
- `copy1()` copies file contents.
- `split()` splits a path into directory and final element, with special handling for `..`.
- `samefile()` compares qid/dev/type.
- `hardremove()` repeatedly removes a target, exiting on first failure.

Notes:
- Directories are not copied across directories; only renamed when possible.
- Append-only targets are removed before create because `create()` will not truncate them.
