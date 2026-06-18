# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.hh

## Purpose

This header declares the C ABI for XrdFfs per-file-descriptor read/write caching.

## Important APIs, Types, and Functions

The public API is `XrdFfsWcache_init()`, `create()`, `destroy()`, `flush()`, `pread()`, and `pwrite()`. These calls wrap descriptor-local cache allocation, invalidation, flushing, and cached I/O.

## Control Flow

FUSE open/create calls initialize a descriptor cache. Reads and writes route through cached pread/pwrite when appropriate. Fsync, truncate, and release call flush before remote synchronization or close.

## State and Persistence Behavior

The header has no state; the implementation owns the global descriptor table. Buffered writes are not durable until flushed.

## Dependencies and Integration Points

It is consumed by `XrdFfsXrootdfs.cc` and implemented by `XrdFfsWcache.cc`.

## Risks and Edge Cases

No include guard is present, and the header uses `ssize_t`, `size_t`, and `off_t` without including their defining system headers. Callers must pass XrdPosix virtual descriptors in the same range configured by `init()`.

## Test Signals

Compile tests should include standalone header checks. Runtime signals come from implementation and FUSE open/read/write/release behavior.
