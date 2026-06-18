# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/sbox.c

`sbox.c` fills/clears a rectangular screen-space box using the current background color. It transforms plot coordinates, normalizes corner order, clips to the clipping rectangle, and calls `m_clrwin()`.
