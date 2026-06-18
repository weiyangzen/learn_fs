# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath.c

Basic path construction and clipping operators. It registers `moveto`, `lineto`, `curveto`, relative variants, `closepath`, `newpath`, `currentpoint`, `clip`, `eoclip`, and `initclip`.

`common_to` reads two numeric operands and dispatches to absolute or relative move/line functions. `common_curve` does the same for six curve operands. `currentpoint` calls `gs_currentpoint` and pushes the current coordinates.

The clipping operators call `gs_clip`, `gs_eoclip`, and `gs_initclip`; path construction calls the corresponding `gspath.h` routines. This file is the basic PostScript path-to-graphics-state binding.
