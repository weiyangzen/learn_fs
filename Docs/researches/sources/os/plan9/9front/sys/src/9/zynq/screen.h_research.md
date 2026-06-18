# File Research: sources/os/plan9/9front/sys/src/9/zynq/screen.h

Purpose: Zynq screen/mouse integration header for portable Plan 9 draw and mouse code.

Key interfaces:
- Mouse declarations: cursor, mouse tracking, acceleration, serial mouse byte handlers, `mousectl`, redraw/resize.
- Screen declarations: blanking, flushing, attaching, cursor operations.
- Draw declarations: `deletescreenimage`, `resetscreenimage`, `drawlock`.
- Defines `ishwimage(i)` as always true for `devdraw.c`.

Integration notes: Included by `screen.c` and expected by draw/mouse drivers.

Risk/attention points: `ishwimage(i) 1` means all images are treated as hardware images in the relevant portable code path.
