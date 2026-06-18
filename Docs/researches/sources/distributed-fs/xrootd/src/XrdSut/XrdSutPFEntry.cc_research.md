# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.cc

## Purpose

This file implements password-file entry buffers and entries. A `XrdSutPFEntry` is the serializable record stored in `XrdSutPFile` and cached by `XrdSutPFCache`.

## Important APIs, types, and functions

`XrdSutPFBuf` owns one byte buffer and supports construction, copy construction, destruction, and `SetBuf`. `XrdSutPFEntry` supports construction with name/status/count/mtime, copy construction, `Reset`, `SetName`, `AsString`, and assignment. The status enum is declared in the header.

## Control flow

Construction duplicates names and buffers. `Reset` clears all fields and refreshes modification time. `AsString` formats a static display string with status/count/buffer sizes/time/name. Assignment should duplicate another entry's metadata and four buffers.

## State and persistence behavior

The entry's fields are the durable state persisted by `XrdSutPFile`: status, count, modification time, and four arbitrary buffers. The name is stored in the file index rather than the entry body, but cache copies hold it on the entry object too.

## Dependencies and integration points

The file depends on `XrdSutAux` for time formatting and is used by `XrdSutPFile` and `XrdSutPFCache`.

## Risks and edge cases

The assignment operator appears to have the same defects as `XrdSutCacheEntry`: it calls `SetName(name)` rather than `SetName(e.name)` and calls `SetBuf(e.bufN.buf)` without the source length, clearing buffers instead of copying them. `AsString` uses a static buffer and `%s` for `name`, so it is not thread-safe and can mishandle null names. `SetBuf` clears old data before allocation, so failures lose previous content.

## Test signals

Tests should verify copy construction, assignment preserving all buffers and names, reset semantics, display formatting, and round-trip persistence through `XrdSutPFile`.
