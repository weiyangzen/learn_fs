# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.cc

## Purpose

This file implements a cache for filesystem space information returned through `statvfs`. XrdFfs uses it to avoid repeatedly querying every XRootD data server for OSS quota/free-space attributes during frequent FUSE `statfs` calls.

## Important APIs, Types, and Functions

The public function is `XrdFfsFsinfo_cache_search(func, rdrurl, path, stbuf, user_uid)`. The supplied `func` has the same signature as `XrdFfsPosix_statvfsall()` and is called on cache misses or refreshes.

Internal `XrdFfsFsInfo` stores timestamp, `f_blocks`, `f_bavail`, and `f_bfree`. `XrdFfsFsinfoHtab` is an `XrdOucHash` keyed by an extracted `oss.cgroup=` token or a single-space default key. Separate reader and writer mutexes gate lookup and periodic updates.

## Control Flow

The function tries to take the writer mutex without blocking, then locks the reader mutex and looks up cached data. A hit copies space fields into `stbuf`; a miss calls the real stat function and creates a candidate record. If this caller acquired the writer lock and the record is older than 120 seconds, it refreshes the value, updates timestamp and counters, and stores nonzero-capacity results back into the hash.

## State and Persistence Behavior

The cache is in-memory and keyed by OSS space token rather than full path. Entries persist until process exit and are refreshed every two minutes by whichever caller obtains the writer mutex. Space tokens with zero blocks are not cached.

## Dependencies and Integration Points

The file depends on `statvfs`, pthreads, and `XrdOucHash`. It is called by the FUSE executable's `xrootdfs_statfs()` and delegates actual collection to `XrdFfsPosix_statvfsall()`.

## Risks and Edge Cases

The key extraction uses `strstr(path, "oss.cgroup=")` and keeps everything after the token, including later query data. Miss handling allocates `s` before knowing whether it will be inserted; only some zero-block miss paths free it. The two-mutex scheme allows stale values during refresh and is not a conventional read/write lock.

## Test Signals

Tests should cover default and `oss.cgroup` keys, hit/miss behavior, refresh after 120 seconds, zero-block non-caching, concurrent callers, and propagation of delegate errors.
