# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.c

Purpose: Implements graphics-state alpha accessors.

Key interfaces: `gs_setalpha` and `gs_currentalpha`.

Control flow: `gs_setalpha` clamps a floating alpha to [0,1], converts it to `gx_color_value`, stores it in the graphics state, and invalidates the current device color. `gs_currentalpha` converts the stored integer alpha back to float.

Dependencies: Uses `gsalpha.h`, `gxdcolor.h`, `gzstate.h`, and `gx_max_color_value`.

Risks and notes: Alpha change correctly unsets cached device color; callers relying on cached colors must expect recomputation.
