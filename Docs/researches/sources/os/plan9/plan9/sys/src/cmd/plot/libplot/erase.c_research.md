# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/erase.c

Clears the current plot window.

Key responsibilities:
- Swaps/flushes any current buffer.
- Clears the clipping rectangle to `e1->backgr`.

Dependencies:
- Uses `m_swapbuf()` and `m_clrwin()` from `machdep.c`.
