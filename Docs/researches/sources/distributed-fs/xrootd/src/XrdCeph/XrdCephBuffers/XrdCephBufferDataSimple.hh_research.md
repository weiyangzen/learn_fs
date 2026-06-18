# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.hh

Purpose: declares a simple vector-backed implementation of `IXrdCephBufferData`.

Important APIs/types/functions: constructor with buffer capacity; overrides capacity, length, validity, starting offset, invalidate, read/write buffer methods, and raw pointer accessors. Static atomics track total memory and live buffer count.

Control flow: algorithms/adapters treat this class as the physical cache storage. Inline `raw()` returns `&m_buffer[0]` only when capacity is nonzero.

State and persistence: per-buffer vector, length, validity, external offset, timer/counter fields, plus static aggregate counters. No disk persistence.

Dependencies and integration points: includes `IXrdCephBufferData`, `BufferUtils`, STL vector/atomic/chrono. Used by the XrdCeph buffered file stack.

Risks: no internal locking; callers must serialize access. Capacity is a separately stored `m_bufferSize`, so vector capacity/size divergence would matter if changed. Static counters are useful for diagnostics but not exposed through a stable API.

Test signals: polymorphic behavior through `IXrdCephBufferData`, raw pointer stability, capacity/length semantics, and thread-safety assumptions under algorithm locking.
