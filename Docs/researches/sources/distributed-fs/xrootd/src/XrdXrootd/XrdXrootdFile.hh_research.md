# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.hh

Purpose: declares the per-open-file object, deferred file-handle processor, and per-link file table used by the xrootd protocol.

Important APIs and types: `XrdXrootdFileHP` stores reusable handles with reference-counted lifetime, `Avail()`, `Delete()`, `Get()`, and `Ref()`. `XrdXrootdFile` exposes SFS pointer, mmap/callback union, file key, mode, async and mmap flags, sendfile state, fd/handle union, AIO/page-write freight pointers, deferred handle processor, user id, and `XrdXrootdFileStats`. Its APIs are `Init()`, `Ref()`, `Serialize()`, constructor, and destructor. `XrdXrootdFileTable` has fixed `FTab[16]`, expandable `XTab`, `Add()`, `Del()`, `Get()`, and `Recycle()`.

Control flow and state: `Get()` rejects `heldSpotP` placeholders. `XrdXrootdFileHP` can outlive the table until all deferred file close operations return handles. `XrdXrootdFile` uses a semaphore pointer to let the destructor wait for request references to drain.

Dependencies and integration: includes protocol wire types, pthread helpers, and file stats. It forward-declares SFS, lock, monitor, and freight classes to keep the header relatively light.

Risks and test signals: external serialization is required for table mutation, so misuse can race with request handlers. Tests should verify `Get()` behavior for invalid and held handles, external table expansion, `XrdXrootdFileHP` deletion with outstanding refs, and reference wait/wakeup.
