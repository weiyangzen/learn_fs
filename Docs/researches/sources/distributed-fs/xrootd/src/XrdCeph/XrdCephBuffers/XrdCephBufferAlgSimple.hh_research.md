# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.hh

Purpose: declares the simple Ceph buffer algorithm concrete class.

Important APIs/types/functions: constructor takes owned `IXrdCephBufferData` and `ICephIOAdapter`, fd, and striperless flag; overrides AIO and sync read/write plus `flushWriteCache`; exposes `buffer()` accessors for review/testing; protected `rawRead/rawWrite` placeholders.

Control flow: public API matches `IXrdCephBufferAlg`; implementation serializes buffer access and controls cache fill/flush.

State and persistence: owns cache memory and IO adapter, tracks fd, buffer range, mutex, and usage stats. Persistent writes are deferred until flush.

Dependencies and integration points: includes interfaces and utilities. It is built into the XrdCeph module and selected by buffered file implementation.

Risks: ownership is mixed with the adapter: comment says no ownership for `m_cephio`, but the type is `unique_ptr`, so it does own it. Exposing mutable `buffer()` can break invariants if external callers modify state without the algorithm mutex.

Test signals: constructor ownership/destruction, buffer accessor invariants, flush semantics, and use with mock IO adapters.
