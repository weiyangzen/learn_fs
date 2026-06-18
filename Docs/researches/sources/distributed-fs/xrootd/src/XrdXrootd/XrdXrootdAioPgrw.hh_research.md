# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.hh

Purpose: declares the page-read/write AIO buffer class used for xrootd page I/O requests. It specializes `XrdXrootdAioBuff` by adding checksum storage and scatter/gather layouts.

Important APIs and types: `Alloc()` returns a page buffer instance. `Setup2Recv()` prepares the object to receive page-write data from a socket and then write file data. `Setup2Send()` prepares file-read data for page-read response framing. `iov4Recv()`, `iov4Send()`, and `iov4Data()` expose `struct iovec` arrays for socket/file transfer stages. `noChkSums()` tests and optionally restores checksum-vector availability. Static constants `aioSZ` and `acsSZ` define the fixed page segment capacity.

Control flow and state: private `csVec[acsSZ]` stores checksums, while `ioVec[acsSZ*2+1]` stores the response/receive layout. `csNum` and `iovReset` are mutable per-operation state, reset across setup calls.

Dependencies and integration: includes xrootd protocol page constants and `XrdXrootdPgrwAio.hh`. It is tied to `XrdSfsAio` through the base class, and to protocol serialization through the iovec-returning APIs.

Risks and test signals: the header exposes low-level buffers where callers must honor returned counts and lengths. Tests should validate maximum segment capacity, short page framing, checksum restoration after `noChkSums()`, and ABI compatibility of the fixed iovec layout.
