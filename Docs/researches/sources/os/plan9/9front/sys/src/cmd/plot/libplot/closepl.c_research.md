# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/closepl.c

`closepl.c` finalizes plotting by calling the machine-dependent `m_finish()`, which in this backend swaps the offscreen buffer to the display.
