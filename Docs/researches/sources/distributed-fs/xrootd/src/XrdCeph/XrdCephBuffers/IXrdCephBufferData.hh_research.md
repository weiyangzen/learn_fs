# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferData.hh

Purpose: defines the physical buffer memory abstraction for Ceph buffering.

Important APIs/types/functions: capacity/length accessors, validity flag accessors, starting offset accessors, `invalidate`, `readBuffer`, `writeBuffer`, and raw const/mutable memory accessors.

Control flow: algorithms use this interface to copy client bytes into/out of a buffer and adapters use `raw()` to pass the backing memory to Ceph IO calls.

State and persistence: no state in the interface. Implementations track memory, current valid data length, and external offset mapping.

Dependencies and integration points: used by IO adapters and algorithms; implemented by `XrdCephBufferDataSimple`.

Risks: raw pointer access bypasses bounds checking, so adapter and algorithm count values must be consistent with `capacity`. `writeBuffer` includes both local offset and external offset, which can be confusing when the algorithm separately tracks `m_bufferStartingOffset`.

Test signals: generic contract tests for capacity, invalidation, bounds checking, raw pointer availability, and offset/length semantics.
