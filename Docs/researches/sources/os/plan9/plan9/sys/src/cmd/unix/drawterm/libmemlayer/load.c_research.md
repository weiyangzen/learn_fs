# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/load.c

Layer-aware wrapper for loading image bytes.

Key function:
- `memload`: selects raw or compressed load function, then loads into direct images, clear layers, save backing, or a temporary image followed by `memdraw`.

Important behavior:
- Direct-to-screen clear-layer loading requires bit alignment from layer delta.
- If save backing exists and alignment is compatible, loads backing then exposes the changed region.
- Uses a temporary image when obscured/unaligned loading cannot be done directly.
