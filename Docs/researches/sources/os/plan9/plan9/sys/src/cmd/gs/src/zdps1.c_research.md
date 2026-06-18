# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps1.c

Implements Level 2 / Display PostScript graphics extensions.

Stroke-adjust operators: `setstrokeadjust` and `currentstrokeadjust`.

Graphics-state object support:
- `gstate`
- `currentgstate`
- `setgstate`
- gstate-aware `copy`

`gstate_check_space()` validates VM store constraints for gstate refs, with a documented workaround that disallows writing into global VM gstates above save level 0. `gstate_unshare()` copy-on-writes saved gstate objects before mutation.

Rectangle operators:
- `.rectappend`
- `rectclip`
- `rectfill`
- `rectstroke`

`rect_get()` accepts either four numeric stack operands or numeric arrays/strings containing rectangle tuples. It uses a small local rectangle array for up to five rectangles and heap allocation beyond that.

`setbbox` writes the user path bounding box through `gs_setbbox()`.

Registered in `zdps1_l2_op_defs`; `zsetbbox()` is exported for user-path support.
