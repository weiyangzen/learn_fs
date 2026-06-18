# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fopen.c

Read completely: 104 lines.

This file implements `fopen`. It parses mode flags, allocates a `FILE`, opens the path with `open`, rejects descriptors too large for `_file`, installs normal file operation hooks, and seeks to end for append mode so `ftell` starts correctly.

Important interactions: uses `__sflags`, `__sfp`, `__sread`, `__swrite`, `__sseek`, and `__sclose`.

Security/reliability notes: open failures release the reserved stream slot; descriptor width is explicitly guarded.
