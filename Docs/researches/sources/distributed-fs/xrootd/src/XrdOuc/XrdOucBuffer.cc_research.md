# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.cc

## Purpose
Implements an aligned buffer pool and movable buffer object used to reduce allocation churn and data copies.

## Important APIs and control flow
`XrdOucBuffPool::XrdOucBuffPool()` normalizes the minimum size to a power-of-two KiB bucket, rounds maximum size to slot increments, and computes per-slot retention limits. `Alloc()` maps a requested size to a slot, reuses a free buffer under `SlotMutex` when available, or allocates a new `XrdOucBuffer` with `posix_memalign()` using page or smaller alignment.

`BuffSlot::~BuffSlot()` deletes all cached free buffers. `BuffSlot::Recycle()` deletes the buffer if the slot already holds enough cached buffers; otherwise it clears data length/offset and pushes it onto the free list.

`XrdOucBuffer(char*,int)` creates a one-time buffer backed by caller-provided `posix_memalign()` memory and a static null pool. `Clone()` allocates from the same pool and copies `doff + dlen` bytes. `Highjack()` allocates a replacement for the current object and swaps state so the returned object owns the original buffer. `Resize()` highjacks and recycles when the size changes.

## State, dependencies, and integration
Pool state is slot metadata, free lists, bucket sizes, and `alignit` from `sysconf(_SC_PAGESIZE)`. Dependencies are `XrdSysMutex`, `XrdSysPlatform`, and POSIX allocation.

## Risks and test signals
`Recycle()` checks `numbuff >= maxbuff` before taking the slot lock, so concurrent recycle can overshoot retention. One-time buffers use a zero-size null pool, making clone/highjack/resize fail as documented. Tests should cover alignment, slot rounding, concurrent allocation/recycle, one-time buffer limitations, clone trimming, and highjack ownership transfer.
