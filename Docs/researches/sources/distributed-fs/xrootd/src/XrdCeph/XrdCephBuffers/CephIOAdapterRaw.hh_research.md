# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.hh

Purpose: declares the synchronous Ceph POSIX IO adapter used by the buffer algorithm.

Important APIs/types/functions: `CephIOAdapterRaw` implements `ICephIOAdapter`; constructor accepts `IXrdCephBufferData *`, fd, and `useStriperlessReads`; overrides `write(off64_t,size_t)` and `read(off64_t,size_t)`.

Control flow: the adapter expects callers to fill or consume the associated buffer object and then call adapter read/write against Ceph offsets.

State and persistence: stores non-owned buffer pointer, fd, striperless-read flag, and stats counters. Persistent data effects occur through Ceph writes.

Dependencies and integration points: includes buffer interfaces, `ICephIOAdapter`, `BufferUtils`, chrono/memory/atomic. It provides the low-level storage bridge for `XrdCephBufferAlgSimple`.

Risks: no ownership semantics are encoded in types; a dangling buffer pointer would be fatal. Stats fields are not all atomic (`longest` values), so concurrent use may race unless externally serialized.

Test signals: construction with valid/invalid buffer, polymorphic use via `ICephIOAdapter`, and concurrent read/write behavior when used behind the algorithm mutex.
