# File Research: sources/os/bsd/netbsd-src/lib/libc/string/index.c

Compatibility wrapper for legacy `index()`. It defines `INDEX` and includes `strchr.c`, causing the shared character-search implementation to emit the `index` variant.

There is no independent logic in this file.
