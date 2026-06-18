# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lorigin.c

Moves a layer’s logical and/or screen origin.

Key functions:
- `memlorigin`: changes logical rectangle origin and screen position, preserving content and exposure behavior.
- `memlnorefresh`: no-op refresh function used for temporary shadow layers.

Important behavior:
- Brings the layer to front before moving.
- Reallocates save backing if logical coordinates change.
- Uses a temporary shadow layer at the old screen rectangle to restore background/expose other layers during movement.
