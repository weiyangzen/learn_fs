# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arctest.c

Small timing/test program for `memarc`.

Key behavior:
- Initializes memdraw, allocates a `CMAP8` image, and repeatedly draws an arc based on `argv[1]`.
- Measures elapsed nanoseconds with a small timing overhead subtraction.
- Provides local `drawdebug`, `rdb`, and `iprint` stubs for standalone testing.
