# File Research: sources/os/plan9/plan9/sys/src/lib9p/util.c

This file provides small read-response helpers for lib9p servers.

Key behavior:
- `readbuf` copies a bounded slice from a memory buffer into `r->ofcall.data` based on request offset/count.
- If offset is past the end, it returns zero bytes.
- If requested data extends past the end, it truncates count.
- `readstr` applies `readbuf` to a NUL-terminated string using `strlen`.

Role:
- Convenience for simple synthetic-file read handlers.
- Does not call `respond`; callers set up data and respond separately.
