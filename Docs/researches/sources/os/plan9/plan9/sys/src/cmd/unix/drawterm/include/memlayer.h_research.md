# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memlayer.h

Plan 9 memory layer/window stacking API.

Key contents:
- Defines `Memscreen` and `Memlayer` for front/rear layer lists, screen rectangles, save areas, clear state, and refresh callbacks.
- Declares layer load/unload, allocation, deletion/free, front/back ordering, refresh setup, hide/expose, clear recomputation, origin movement, and no-refresh callback.

Role in this group:
- Supports Plan 9-style window/layer behavior on top of `Memimage`.

Notable risks:
- Functions distinguish local coordinates from screen coordinates; misuse can corrupt layer positioning.
