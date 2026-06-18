# File Research: sources/local-fs/xfsdump/invutil/invutil.h

Shared header for `xfsinvutil` command and interactive inventory utility modules.

Defines:
- String buffer constants `STR_LEN` and `GEN_STRLEN`.
- `SYSCALL_FAILED` and `LOCK_BUSY` return codes for `open_and_lock()`.
- `Open_t`, describing read/write/unsafe modes for files and directories.

Exports:
- program globals: `g_programName`, `g_programVersion`, `inventory_path`.
- mode globals: `debug`, `force`, `wait_for_locks`.
- inventory path helpers, pruning functions, mmap/read/write helpers, listing functions, interactive entry point, and mountpoint comparison.

Role:
- Central coordination header tying command-line pruning, interactive UI, and inventory storage-object traversal together.
