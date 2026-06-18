# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/line.c

Layer-aware wrapper for line drawing.

Key functions:
- `_memline`: handles direct image lines or subdivides layered destination lines by bounding box.
- `llineop`: callback that remaps coordinates for save areas and recursively draws clipped line pieces.
- `memline`: public wrapper using destination clipr.

Important behavior:
- Layered sources are unsupported for line drawing.
- Clips source constraints once before converting destination coordinates to screen space.
- Uses `memlinebbox` to choose the subdivision region because wide lines cannot be simple Cohen-Sutherland clipped.
