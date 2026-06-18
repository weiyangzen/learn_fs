# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/listalloc.c

This file implements a simple fixed-size free-list allocator.

Key routine:
- `listalloc(n, size)` rounds `size` up to pointer alignment, allocates `n * size` bytes, and chains the elements by storing a next pointer at the start of each item.

Important interactions:
- Declared in `fns.h`; intended for subsystems needing bulk allocation of list nodes.

Research notes:
- The caller receives the base pointer, with each element internally linked.
- No free routine is provided here.
