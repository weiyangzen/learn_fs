# File Research: sources/local-fs/xfsdump/restore/node.c

## Summary
Implements a persistent, mmap-windowed node allocator used by the restore tree. Nodes are addressed by 32-bit handles and stored in segments inside a housekeeping file.

## Main Responsibilities
- Initialize or resync persistent node allocator metadata.
- Choose segment size, nodes-per-segment, and window count from node size, alignment, estimated inode count, and virtual memory budget.
- Allocate nodes from a free list or a virgin node counter.
- Map node handles to memory through the `win` abstraction.
- Free nodes back to a singly-linked free list.
- Optionally validate handles and node state when compiled with `NODECHK`.

## Important Behavior
`node_init()` rounds user node size up to alignment, picks a power-of-two `nodesperseg`, ensures at least `WINMAP_MIN` windows can fit in available virtual memory, mmaps the allocator header, initializes persistent fields, and calls `win_init()`.

`node_sync()` mmaps an existing node header and reinitializes the window abstraction using persisted segment parameters.

`node_alloc()` first reuses `nh_freenh` if available. Otherwise it takes `nh_virgnh`, pre-grows a new segment with `ftruncate64()` when entering a segment, and returns the handle unless it exceeds `NH_MAX`.

`node_map()` uses bit shifts and masks to split a handle into segment index and node index, then delegates segment mapping to `win_map()`.

`node_free()` writes the old free-list head into the freed node’s first word, updates `nh_freenh`, unmaps the node, and clears the caller’s handle.

## Dependencies
Depends on page-size globals, `mmap_autogrow()`, `win`, xfsdump types/logging, and optional `NODECHK` validation macros.

## Risks
The allocator uses the beginning of each node for free-list linkage and requires the caller to reserve a housekeeping byte; callers must honor the layout constraints passed to `node_init()`.

A failed segment `ftruncate64()` is logged as a warning but allocation continues, relying on later mmap/autogrow behavior.

Most structural errors are assertions. With assertions disabled, stale handles or corrupted persistent state could cause wrong mappings or list corruption.

Handle capacity is capped by `nh_t`; very large restores can return `NH_NULL` when node count exceeds `NH_MAX`.
