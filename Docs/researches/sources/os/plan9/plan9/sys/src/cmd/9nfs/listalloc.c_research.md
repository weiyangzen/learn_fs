# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/listalloc.c

Purpose: fixed-size freelist allocator helper.

Key behavior: rounds element size to `ulong` alignment, allocates `n` elements, and links them by storing next pointers in each slot.

Integration notes: returns a raw freelist head; callers must know element layout and manage allocations themselves.
