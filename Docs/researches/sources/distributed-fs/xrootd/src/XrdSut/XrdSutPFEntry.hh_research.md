# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.hh

## Purpose

This header declares the password-file entry record used by XrdSut credential files and caches.

## Important APIs, types, and functions

`kPFEntryStatus` defines inactive, disabled, allowed, ok, one-time, expired, special, anonymous, and crypt states. `XrdSutPFBuf` stores one arbitrary byte buffer. `XrdSutPFEntry` stores name, status, count, modification time, four buffers, and an entry mutex. It exposes `Length`, `Reset`, `SetName`, `AsString`, and assignment.

## Control flow

`XrdSutPFile` serializes/deserializes these entries, while `XrdSutPFCache` locks and returns them for credential validation/update. Callers mutate public fields directly.

## State and persistence behavior

The entry's non-name fields are serialized into PFile entry records. Name is used as the index key. The mutex is runtime-only and not copied to disk.

## Dependencies and integration points

It depends on protocol integer types and XrdSys mutexes. It is included by password-file cache and file interfaces and by security protocol code that reads credentials.

## Risks and edge cases

Public fields make serialization invariants caller-managed. The mutex must be respected by cache users. `Length` must stay in sync with `XrdSutPFile::WriteEnt` and `ReadEnt`; changing either side breaks on-disk compatibility.

## Test signals

Compatibility tests should assert `Length` for known buffer sizes, status numeric values, and PFile round-trip compatibility across versions.
