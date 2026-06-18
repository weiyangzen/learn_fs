# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.cc

## Purpose

This file implements the small object pool for `XrdXrootdPio`, the protocol's queued parallel-I/O descriptor. The pool reduces allocation churn for offloaded reads/writes and bound-stream I/O operations.

## Important APIs, types, and functions

`XrdXrootdPio::Alloc(int Num)` returns a linked list of at least `Num` cleared descriptors. `Recycle()` clears one descriptor and either pushes it to a static free list or deletes it when `FreeMax` cached entries already exist. Static members are `myMutex`, `Free`, and `FreeNum`.

## Control flow

Allocation first drains as many descriptors as possible from the free list under `myMutex`, detaches the returned chain, then allocates additional descriptors with `new` until the requested count is satisfied. Recycling locks the same mutex, checks the cache cap, clears the descriptor using `Clear(Free)`, and links it back onto the free list.

## State and persistence behavior

The only state is process-local pool state. Descriptors carry no durable data; `Clear()` zeros the resume pointer, `IOParms`, stream id, and next pointer before reuse.

## Dependencies and integration points

The implementation depends on `XrdXrootdPio.hh` and indirectly on `XrdXrootdProtocol`/`IOParms`. `XrdXrootdProtocol::Cleanup()` recycles active and free per-link PIO objects; execution paths in `XrdXrootdXeq.cc` allocate them for parallel stream/offload work.

## Risks and edge cases

The pool is global and bounded but never shrinks below objects already retained, so tests that expect exact allocation counts must account for reuse. `Alloc(0)` can still return the current free head if misused because the code checks `Free` before consuming `Num`; callers should pass positive counts. Descriptor ownership is manual and double recycling would corrupt the free list.

## Test signals

Useful tests cover allocating from empty and populated pools, clearing stale `IOParms` and stream ids, respecting `FreeMax`, and running recycle/allocation under concurrent worker threads.
