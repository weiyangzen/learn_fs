# File Research: sources/local-fs/squashfs-tools/squashfs-tools/error.h

Shared error/logging macro header.

Declares:
- `progressbar_error()`
- `progressbar_info()`
- `pre_exit_squashfs()`

Defines:
- `TRACE()` under `SQUASHFS_TRACE`, otherwise no-op.
- `ERROR()` as progressbar error logging.
- `MEM_ERROR()` as fatal out-of-memory logging plus `pre_exit_squashfs()` and `exit(1)`.
- `BAD_ERROR()` as fatal internal/error logging plus cleanup and exit.

Notable quirk:
- The include guard ends before `MEM_ERROR` and `BAD_ERROR`, so those macros are outside the guard and can be reprocessed on repeated includes.
