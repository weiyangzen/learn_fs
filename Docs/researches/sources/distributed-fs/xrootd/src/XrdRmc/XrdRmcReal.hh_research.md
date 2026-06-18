# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.hh

## Purpose

`XrdRmcReal.hh` declares the concrete `XrdOucCache` implementation used by RMC and exposes internals needed by `XrdRmcData`.

## Important APIs, Types, And Functions

- Public `Attach()`, constructor, destructor, and worker `PreRead()` implement the `XrdOucCache` lifecycle.
- Private cache operations include `Detach()`, `Get()`, `Ref()`, `Trunc()`, `Upd()`, `PreRead(prTask*)`, and I/O tracking helpers.
- Constants `Shift`, `Strip`, and `MaxFO` encode the logical address format: high bits identify the attached file namespace and low bits identify file offsets.
- Fields hold cache geometry, slot arrays, hash tables, file-slot free list, debug/log flags, attach deletion semaphores, and preread queue state.

## Control Flow

The header establishes `XrdRmcData` as a friend and collaborator. Data wrappers call private methods to fault pages, release references, and enqueue prereads while the cache controls global memory and slot ownership.

## State And Persistence

The class owns all process-memory cache state. It has no persistence contract beyond the lifetime of the `XrdRmcReal` object.

## Dependencies And Integration Points

It includes `XrdRmc.hh`, `XrdRmcSlot.hh`, and `XrdSysPthread.hh`, and implements the `XrdOucCache` API from `XrdRmc.hh`.

## Risks And Edge Cases

- The logical address format limits file offset range to `MaxFO`.
- The private hash/list machinery is not encapsulated behind standard containers, so callers must not bypass the `XrdRmcData` protocol.
- Preread task nodes are embedded in `XrdRmcData`; queue validity depends on wrapper lifetime coordination.

## Test Signals

Header-level tests should compile the class through `XrdRmc::Create()` and exercise behavior via the public `XrdOucCache` API. Concurrency tests should stress `Get`, `Ref`, and preread queue interactions.
