# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltofront.c

Moves layers toward the front of the screen stack.

Key functions:
- `_memltofront`: swaps a layer forward until it reaches the requested front marker, hiding overlapped front layers and optionally exposing the moved layer.
- `_memltofrontfill`: internal front move with optional exposure fill.
- `memltofront`: public single-layer move.
- `memltofrontn`: moves multiple layers while preserving caller-specified relative order.

Important behavior:
- Updates `frontmost`/`rearmost` and neighboring `front`/`rear` links during each swap.
- Recomputes clear flags after ordering changes.
