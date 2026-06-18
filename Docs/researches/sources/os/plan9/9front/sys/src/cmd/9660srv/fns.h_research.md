# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/fns.h

Function declarations and error-stack macros for `9660srv`.

Key contents:
- Declares shared helpers for logging, allocation, error raising, buffer cache operations, backing-device lookup, server panic, filesystem refcounting, directory display, fid lookup, and `Dir` name-buffer setup.
- Defines `waserror()` and `poperror()` wrappers around the global `jmp_buf` stack.

Filesystem relevance: direct support header for the ISO 9P filesystem server.
