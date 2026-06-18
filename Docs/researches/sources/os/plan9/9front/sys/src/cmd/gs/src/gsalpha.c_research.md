# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.c

Purpose: Graphics-state alpha accessor implementation.

Key behavior: `gs_setalpha` clamps a floating alpha to `[0,1]`, converts it to `gx_color_value`, stores it in `pgs->alpha`, and invalidates the current device color. `gs_currentalpha` converts the stored fixed color value back to float.

Dependencies and notes: Small standalone implementation so alpha state can be initialized even when full alpha compositing is not built.
