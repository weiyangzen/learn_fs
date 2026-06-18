# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.hh

## Purpose

This header exposes the C ABI for XrdFfs filesystem-space cache lookup. It lets FUSE code call a cached wrapper around a supplied `statvfs` fan-out implementation.

## Important APIs, Types, and Functions

`XrdFfsFsinfo_cache_search()` accepts a function pointer, redirector URL, path, output `statvfs`, and user uid. The function pointer contract matches `XrdFfsPosix_statvfsall()`.

## Control Flow

Callers initialize the block size fields in `stbuf`, then call this function. The implementation either fills block/free counters from cache or delegates to the supplied function.

## State and Persistence Behavior

The header itself stores no state; the implementation owns a global in-memory hash.

## Dependencies and Integration Points

It includes `sys/statvfs.h` and is consumed by `XrdFfsXrootdfs.cc`.

## Risks and Edge Cases

The header has no include guard and uses `uid_t` without explicitly including `sys/types.h`, relying on transitive platform headers. The function pointer ABI must stay synchronized with `XrdFfsPosix_statvfsall()`.

## Test Signals

Compile tests should include the header standalone where possible. Runtime tests come from the implementation and FUSE `statfs` paths.
