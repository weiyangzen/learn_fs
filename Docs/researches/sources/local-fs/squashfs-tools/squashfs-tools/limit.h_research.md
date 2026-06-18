# File Research: sources/local-fs/squashfs-tools/squashfs-tools/limit.h

Header for file-descriptor limit handling.

Defines:
- `OPEN_FILE_MARGIN 10`

Exports:
- `file_limit()`

Key role: centralizes the safety margin kept below `RLIMIT_NOFILE`.
