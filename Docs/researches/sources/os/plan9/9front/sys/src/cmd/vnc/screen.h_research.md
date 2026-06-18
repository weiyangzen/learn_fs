# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/screen.h

## Role

`screen.h` declares the VNC server in-memory screen, cursor, mouse, and draw-device integration surface.

## Contents

- Declares `Cursorinfo`, global `cursor`, `arrow`, `gscreen`, `cursorver`, and `cursorpos`.
- Declares cursor operations, screen flush/attach/delete/reset operations, color hooks, blanking, mouse tracking, and `fsinit()`.
- Declares global `drawlock` and `drawactive()`.
- Defines `TK2SEC(x)` as zero and `ishwimage(i)` as zero for this user-space softscreen environment.

## Notable Limitations And Risk Areas

- Some declarations are compatibility placeholders for code adapted from kernel/drawterm contexts.
- `ishwimage()` always false, so draw paths avoid hardware-image special behavior except where guarded separately.
