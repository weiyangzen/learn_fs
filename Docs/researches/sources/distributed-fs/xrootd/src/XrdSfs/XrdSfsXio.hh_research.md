# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.hh

## Purpose
Defines the exchange-buffer I/O interface that lets SFS file implementations claim or swap server I/O buffers to reduce data copying on writes.

## Important APIs, Types, And Functions
- `XrdSfsXioHandle` is an `XrdBuffer *` handle.
- Static `Buffer(handle, size*)` obtains a buffer address and size.
- `Claim(curBuff, datasz, minasz)` transfers ownership of the current buffer when efficient.
- Static `Reclaim(handle)` returns a claimed/swapped buffer.
- `Swap(curBuff, oldHand)` atomically takes ownership of the current buffer and optionally returns a previous one.

## Control Flow
When a file supports exchange I/O, the server calls `setXio()` on the `XrdSfsFile`. During write handling, the filesystem can `Claim()` the current buffer or `Swap()` it with a previous handle. Later it calls static `Reclaim()` when ownership should return to the framework.

## State And Persistence
The abstract object itself has no state beyond the static implementation installed by construction. Handles represent transient buffer ownership, not persistent file data.

## Dependencies And Integration Points
Forward-depends on `XrdBuffer` and `XrdSfsXioImpl`. Tied to `XrdSfs::hasSXIO` feature advertisement and `XrdSfsFile::setXio()`.

## Risks And Edge Cases
Incorrect `curBuff` matching returns `EINVAL`, memory pressure can return `ENOBUFS`, and unsupported contexts return `ENOTSUP`. Failure to reclaim handles leaks buffers. This API is write-oriented and not a general read-buffer exchange mechanism.

## Test Signals
Mock implementations should cover successful claim/swap/reclaim, stale current-buffer pointers, old-handle replacement, memory-waste rejection with `errno == 0`, and file close cleanup of outstanding handles.
