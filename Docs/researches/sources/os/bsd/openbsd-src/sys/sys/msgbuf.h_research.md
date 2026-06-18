# File Research: sources/os/bsd/openbsd-src/sys/sys/msgbuf.h

Defines kernel console/message ring buffer layout.

Key contents:
- `struct msgbuf` with magic, write/read offsets, size, dropped-byte count, and flexible buffer byte storage.
- Locking annotations reference `log_mtx`.
- `MSG_MAGIC` and `CONSBUFSIZE`.

Kernel APIs:
- Globals `msgbufp` and `consbufp`.
- `initmsgbuf()`, `initconsbuf()`, `msgbuf_putchar()`.

Risk notes:
- The buffer is a low-level diagnostic path; incorrect size or pointer initialization can lose boot/kernel messages.
