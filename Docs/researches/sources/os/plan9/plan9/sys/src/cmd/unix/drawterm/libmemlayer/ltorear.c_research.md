# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltorear.c

Moves layers toward the rear of the screen stack.

Key functions:
- `_memltorear`: swaps a layer backward until it reaches the requested rear marker, hiding the moved layer where overlapped and exposing layers moved above it.
- `memltorear`: public single-layer move.
- `memltorearn`: moves multiple layers while preserving relative order.

Important behavior:
- Maintains doubly linked layer stack pointers and screen `frontmost`/`rearmost`.
- Recomputes clear flags after ordering changes.
