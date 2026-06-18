# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwln.c

Read completely: 120 lines.

This file implements `fgetwln`, a wide-character analogue of `fgetln`. It locks the stream, sets wide orientation, reads with `__fgetwc_unlock` until newline or WEOF, grows the stream extension line buffer in 512-wide-character chunks, and returns the buffer with a length count.

Important interactions: reuses `_EXT(fp)->_fgetstr_buf` as wide storage and depends on `__fgetwc_unlock`.

Security/reliability notes: allocation failure sets `__SERR`; returned buffer is not necessarily NUL-terminated and is stream-owned.
