# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/draw.c

Layer-aware wrapper for `memdraw`.

Key functions:
- `memdraw`: handles direct images, layered destinations, layered sources, clear layers, obscured layers, save areas, and same-layer moves.
- `ldrawop`: callback used by `_memlayerop` to draw either onto the screen image or a layer save image.

Important behavior:
- Layered masks are rejected as too hard.
- Converts between logical layer coordinates and screen coordinates using `Memlayer.delta`.
- Same-layer overlapping draws hide/expose affected regions and draw in backing store when possible.
