# File Research: sources/teaching/os161/kern/include/kern/limits.h

Defines private-name system limits exported to userland/kernel wrappers.

Key limits:
- `__NAME_MAX` 255, `__PATH_MAX` 1024, `__ARG_MAX` 64 KiB.
- PID range, `__OPEN_MAX` 128, `__PIPE_BUF` 512.
- Groups/login/iovec limits.

Relevance:
- Path and filename limits complement filesystem-specific `SFS_NAMELEN`.
- Public `<limits.h>` maps these private names to standard names.
