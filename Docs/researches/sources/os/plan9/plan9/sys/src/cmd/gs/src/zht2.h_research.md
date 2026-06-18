# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.h

Small shared header for Level 2 halftone support. It includes `gscspace.h` for `gs_separation_name` and declares `gs_get_colorname_string`, which converts a separation/colorant name index into string data and length.

The function is implemented in `zht2.c` and is stored in multiple halftone structures so lower-level halftone code can resolve component names without depending directly on interpreter `ref` objects.
