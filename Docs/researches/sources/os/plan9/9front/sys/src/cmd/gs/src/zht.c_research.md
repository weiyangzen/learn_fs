# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht.c

## Purpose
Implements basic halftone and screen operators, including `.currenthalftone`, `.currentscreenlevels`, and `setscreen`.

## Key Functions
- `zcurrenthalftone()` returns screen, colorscreen, or dictionary halftone state.
- `zcurrentscreenlevels()` exposes the current screen level count.
- `zsetscreen()` initializes a screen order and starts spot-function sampling.
- `zscreen_enum_init()` sets up execution-stack state for sampling screen cells.
- `screen_sample()` and `set_screen_continue()` drive repeated calls to the PostScript spot function.
- `setscreen_finish()` installs the completed screen.

## Important Behavior
- `setscreen` samples each cell of a halftone pattern by calling user PostScript code.
- The screen enumerator is allocated in the same VM space as the supplied procedure.
- Completion stores the sampled procedure for all color components and clears explicit halftone dictionary state.

## Research Notes
Core continuation-driven halftone sampling path shared by other halftone files.
