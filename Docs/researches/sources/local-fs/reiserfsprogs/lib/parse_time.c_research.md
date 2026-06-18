# File Research: sources/local-fs/reiserfsprogs/lib/parse_time.c

Parses tool timestamp strings. The special string `"now"` returns `time(NULL)`. Otherwise it parses `YYYYMMDDHHMMSS` using `strptime()` when available, or `sscanf()` fallback with range checks, then returns `mktime(&ts)`. Invalid parse state emits `reiserfs_warning()`.
