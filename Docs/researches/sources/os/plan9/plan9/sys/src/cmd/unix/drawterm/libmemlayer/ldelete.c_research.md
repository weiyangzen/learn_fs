# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ldelete.c

Deletes or frees layers.

Key functions:
- `memldelete`: frees backing store/refresh state, pushes layer to rear, repaints exposed background if needed, unlinks screen stack, and frees image/layer.
- `memlfree`: frees structures without graphical updates.
- `_memlsetclear`: recomputes whether each layer is fully visible and unobscured within the screen clip rectangle.

Important behavior:
- Uses `memltorear` to expose layers above before final unlinking.
- `clear` is invalidated when any front layer overlaps.
