# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetstr.c

Read completely: 66 lines.

This file implements internal `__fgetstr`, the shared line/string reader for `fgetln`. It calls `__getdelim` on the stream extension's reusable `_fgetstr_buf` and `_fgetstr_len`, reports the byte count, and fixes `EOVERFLOW` to `EINVAL` for `fgetln` compatibility.

Important interactions: uses `_EXT(fp)` storage from `fileext.h`.

Security/reliability notes: returned memory is owned by the stream extension and reused.
