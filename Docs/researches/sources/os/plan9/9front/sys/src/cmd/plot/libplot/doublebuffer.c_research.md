# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/doublebuffer.c

`doublebuffer.c` enables backend double buffering by calling `m_dblbuf()`. With buffering enabled, drawing is kept offscreen until an explicit swap.
