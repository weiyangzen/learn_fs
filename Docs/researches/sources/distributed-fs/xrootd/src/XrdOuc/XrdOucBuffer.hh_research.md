# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.hh

## Purpose
Declares `XrdOucBuffPool` and `XrdOucBuffer`, a small buffer-management layer for XRootD utility code.

## Important APIs and types
`XrdOucBuffPool` exposes `Alloc()` and `MaxSize()`. Its constructor parameters control minimum/maximum buffer size, minimum/maximum retained buffers, and reduction rate for larger buckets. Nested `BuffSlot` stores a mutex, free-list head, slot size, current retained count, and maximum retained count.

`XrdOucBuffer` exposes `Buffer()`, `BuffSize()`, `Data()`, `Data(int&)`, `DataLen()`, `SetLen()`, `Clone()`, `Highjack()`, `Resize()`, and `Recycle()`. The public constructor creates a one-time buffer from caller-owned aligned storage that will be freed by the buffer object.

## State, dependencies, and integration
The buffer object tracks raw memory, data length, data offset, total size, slot index, and either free-list next pointer or owning pool pointer via a union. It includes `XrdOucChain.hh` and `XrdSysPthread.hh`, though the chain type is not directly used in this header.

## Risks and test signals
Users must call `Recycle()` rather than `delete`, and must not destroy a pool before outstanding buffers return. Since `SetLen()` does not bounds-check, callers can create invalid data windows. Tests should verify documented allocation size limits, one-time buffer caveats, and misuse behavior under sanitizers.
