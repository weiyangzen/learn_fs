# File Research: sources/local-fs/squashfs-tools/squashfs-tools/limit.c

Implements open-file limit detection.

Main function:
- `file_limit()`

Behavior:
- Caches the computed limit in static `max_files`.
- Calls `getrlimit(RLIMIT_NOFILE)`.
- If lookup fails, logs an error and returns 1.
- If finite, subtracts `OPEN_FILE_MARGIN` unless that would leave no usable files.
- If infinite, returns `-1`.

Key role: provides a conservative maximum number of files the tools should keep open concurrently.
