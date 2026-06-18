# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/circ.c

`circ.c` draws an unfilled circle. It converts the center with `SCX`/`SCY`, converts radius with `SCR`, treats negative radii as positive, and delegates to `m_circ()` with the current foreground color.
