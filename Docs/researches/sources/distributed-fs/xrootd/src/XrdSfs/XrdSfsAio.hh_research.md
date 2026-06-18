# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsAio.hh

## Purpose
Defines the abstract asynchronous I/O completion object used by SFS file implementations. It wraps a POSIX `aiocb` or a compatibility fallback and adds XRootD-specific completion callbacks and checksum-vector support.

## Important APIs, Types, And Functions
- `XrdSfsAio` contains `sfsAio`, `cksVec`, `Result`, and `TIdent`.
- `doneRead()`, `doneWrite()`, and `Recycle()` are pure virtual callbacks implemented by users of the interface.
- A minimal local `struct aiocb` is supplied when `_POSIX_ASYNCHRONOUS_IO` is unavailable.

## Control Flow
Constructing `XrdSfsAio` initializes the POSIX signal event payload to point back to the object, sets `SIGEV_SIGNAL`, zeroes the request priority, clears the checksum vector pointer, and sets an empty trace identifier. File implementations fill `sfsAio`, execute or schedule work, store the result, and invoke the relevant completion callback.

## State And Persistence
Instances carry request-local state only. `Result` uses nonnegative byte/result values and negative errno-style failures by convention. The class does not own buffers or persist data.

## Dependencies And Integration Points
Included by SFS file implementations and used by `XrdSfsInterface.cc` page I/O defaults and `XrdSfsNative.cc` synchronous AIO emulation. Depends on POSIX signal/AIO headers where available.

## Risks And Edge Cases
- The fallback `aiocb` is only a compile-time compatibility structure; it does not imply real OS AIO support.
- Callback ownership is external. Incorrect `Recycle()` behavior or buffer lifetime can corrupt async completions.
- Platform-specific `sigval_ptr` versus `sival_ptr` handling is guarded for older Apple SDKs.

## Test Signals
Compile on platforms with and without `_POSIX_ASYNCHRONOUS_IO`. Unit-test implementations should verify callback invocation, `Result` propagation, checksum vector use for page I/O, and object recycle ownership.
