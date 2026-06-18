# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/help.c

## Purpose
`help.c` implements ss command help lookup and management of per-invocation info directories.

## Important APIs, Types, and Functions
Public functions are `ss_help()`, `ss_add_info_dir()`, and `ss_delete_info_dir()`.

## Control Flow
`ss_help()` lists requests for bare `help`, validates one-topic usage, searches configured info directories for `<topic>.info`, forks a pager with the file on stdin, and waits for it. Directory add validates with `opendir()` and appends to the invocation list; delete removes a matching string.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.info_dirs`. Dependencies include filesystem access, fork/wait, `ss_page_stdin()`, and ss error reporting. Risks include help filename construction without escaping, memory leaks in delete path for removed strings, waiting for wrong child behavior in loops, and no pager error propagation. Test signals are help listing, topic lookup through added directories, and expected `NO_INFO_DIR` or not-found errors.
