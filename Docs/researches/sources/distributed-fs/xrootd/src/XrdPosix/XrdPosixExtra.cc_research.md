## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.cc

Purpose: implements non-standard extended XrdPosix APIs for file/filesystem control queries and page read/write operations with checksums and optional async callbacks.

Important APIs/functions: `Fctl`, `FSctl`, `pgRead`, `pgWrite`, and two `PreRead` overloads.

Control flow: `Fctl()` currently supports `QFinfo`, resolves the descriptor to `XrdPosixFile`, then calls the file/cache I/O `Fcntl()`. `FSctl()` supports `QFSinfo`, optionally routes to global cache `Fcntl()`, otherwise constructs `XrdPosixAdmin`, optionally stats first for redirect resolution, and queries filesystem info. `pgRead()`/`pgWrite()` resolve and lock the file, validate size fits signed 32-bit, manage checksum vectors, dispatch sync through `XCio` or async by setting `cbp->theFile`, taking a file reference, and releasing the lock.

State and persistence: no durable state. Async calls temporarily extend file lifetime by reference. `pgWrite()` updates cached size on sync success.

Dependencies/integration: uses `XrdOucCacheOp`, `XrdOucPgrwUtils`, `XrdPosixObject::File`, `XrdPosixFile`, `XrdPosixCallBackIO`, global cache and thread-local `ecMsg`.

Risks: `PreRead()` is effectively a stub returning success after descriptor validation. Async invalid-FD path calls `Complete(-1)` without setting `errno` locally. Checksum vector count validation is important for partial pages. `Fctl()` comment is truncated in source.

Test signals: `QFinfo` on valid/invalid FD; `QFSinfo` via cache and direct admin; pgread force checksum behavior; pgwrite generated and caller-provided checksums; async callback lifetime; oversized I/O returns `EOVERFLOW`.
