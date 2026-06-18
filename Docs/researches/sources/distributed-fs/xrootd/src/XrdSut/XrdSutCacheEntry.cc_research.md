# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.cc

## Purpose

This file implements generic in-memory cache entry buffers and entries. These mirror the persistent-file entry shape but use `XrdSysRWLock` for shared/exclusive access.

## Important APIs, types, and functions

`XrdSutCacheEntryBuf` owns an optional byte buffer and supports construction, copy construction, destruction, and `SetBuf`. `XrdSutCacheEntry` supports construction with name/status/count/mtime, copy construction, `Reset`, `SetName`, `AsString`, and assignment.

## Control flow

Constructors duplicate names and buffers when present. `Reset` clears the name, status, count, timestamp, and all buffers. `AsString` formats status/count/buffer lengths/modification time/name into a static display buffer. Assignment should copy all fields and buffers from another entry.

## State and persistence behavior

State is in-memory only: name, status, count, modification time, four buffers, and a read/write lock declared in the header. No disk I/O occurs.

## Dependencies and integration points

The file uses `XrdSutTimeString` from `XrdSutAux` and is used by `XrdSutCache`. The entry status enum in the header encodes inactive/disabled/allowed/expired/ok/special semantics for consumers.

## Risks and edge cases

The assignment operator appears defective: it calls `SetName(name)` instead of `SetName(e.name)` and calls `SetBuf(e.bufN.buf)` without passing `e.bufN.len`, so buffers are cleared rather than copied. `AsString` returns a static buffer and is not thread-safe. It also formats `name` with `%s` even if name is null. `SetBuf` clears existing data before allocation, so allocation failure loses the previous value.

## Test signals

Tests should cover deep copy construction, assignment preserving name and buffers, reset clearing all buffers, `AsString` with null and non-null names, and concurrent access patterns through `XrdSutCache`.
