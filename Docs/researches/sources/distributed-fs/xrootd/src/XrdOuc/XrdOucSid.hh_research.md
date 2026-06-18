# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.hh

Purpose: declares `XrdOucSid`, a fast stream ID generator backed by a bit vector.

Important APIs, types, and functions: `theSid` overlays a `short` and two bytes for protocol-friendly SID transfer. Public methods are `Obtain()`, `Release()`, and `Reset()`. The constructor accepts local capacity, optional internal locking, and optional global overflow pool.

Control flow: a connection can allocate a local SID object sized for expected concurrent streams and pass a global pool for overflow. IDs should be released when streams complete so bits can be reused.

State and persistence: private state includes an `XrdSysMutex`, global pool pointer, allocated bit vector, free cursor, vector sizing, max ID count, and lock flag. State is process memory only.

Dependencies and integration points: includes `XrdSysPthread.hh` and is used by stream/multiplexing code that exchanges two-byte IDs.

Risks and test signals: the API accepts raw `theSid*` casts, so endian and signed-short handling must match protocol expectations. The class is not copy-safe. Tests should verify byte representation, allocation order, release reuse, and local/global ID boundaries.
