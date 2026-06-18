# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/doublebuffer.c

Enables libplot double buffering.

Key responsibilities:
- Calls `m_dblbuf()` to allocate and use an offscreen image when possible.

Dependencies:
- Buffer allocation and swap behavior live in `machdep.c`.
