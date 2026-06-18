# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/freopen.c

Read completely: 188 lines.

This file implements `freopen`. It parses new mode flags, flushes and closes the old stream as required, opens the replacement path, tries to preserve the original descriptor with `dup2`, releases old buffers/ungetc/wide state, installs normal file hooks, and seeks to end for append mode.

Important interactions: shares flag parsing and standard file hooks with `fopen`.

Security/reliability notes: tries a second open after closing the old descriptor on `ENFILE`/`EMFILE`; if reopening fails, the original stream slot is freed.
