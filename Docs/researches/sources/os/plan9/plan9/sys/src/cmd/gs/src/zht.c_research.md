# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht.c

Basic halftone/screen operators. It implements `currenthalftone`, `currentscreenlevels`, `setscreen`, and internal continuations for sampling a spot function into a halftone order.

`currenthalftone` reconstructs a PostScript dictionary for the current halftone, while `currentscreenlevels` reports the number of gray levels in the current screen. `zscreen_params` extracts `Frequency`, `Angle`, and `SpotFunction` operands into a `gs_screen_halftone`.

`zsetscreen` prepares screen sampling and calls `zscreen_enum_init`, which pushes a screen-enumeration state on the execution stack. `screen_sample` repeatedly calls the PostScript spot function at coordinates supplied by `gs_screen_currentpoint`; `set_screen_continue` feeds sampled values back into the screen enumerator; `setscreen_finish` installs the final halftone; and `screen_cleanup` tears down aborted enumeration. The file is continuation-heavy because screen sampling calls user PostScript code.
