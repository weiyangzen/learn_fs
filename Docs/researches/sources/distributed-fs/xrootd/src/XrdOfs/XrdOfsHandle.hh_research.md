# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.hh

## Purpose

This header declares private OFS handle data structures. They are used to manage shared storage-system file handles, per-path lookup, reference counts, POSC metadata, and retirement callbacks.

## Important APIs, types, and functions

`XrdOfsHanKey` stores path value, link count, CRC hash, and length, with equality based on hash, length, and string content. `XrdOfsHanTab` provides add/find/remove and hash-table expansion. `XrdOfsHandle` exposes state flags for pending sync, changed file, compression, and read-write mode; allocation and retirement APIs; POSC APIs; storage selection; suppression; usage count; and explicit locking. `XrdOfsHanCB` is the callback interface for deferred retirement.

## Control flow

Callers allocate a handle, attach an OSS object with `Activate()`, operate on `Select()`, then retire it when done. POSC callers set creator metadata while holding the handle lock and retrieve/remove it during close or recovery. Deferred retirement invokes `XrdOfsHanCB::Retired()` when the background expiry thread reaches the handle.

## State and persistence behavior

Static members maintain global tables and free lists. Per-handle state includes mutex, selected OSS object, table linkage, key, and POSC pointer. The header itself does not persist data; POSC queue offsets link it to the separate durable queue.

## Dependencies and integration points

It depends on CRC and XRootD pthread wrappers and forward-declares OSS/file callback support. It is tightly coupled to `XrdOfsHandle.cc`, OFS file open/close code, `XrdOssDF`, and POSC recovery handling.

## Risks and test signals

`XrdOfsHanKey::operator=` duplicates `Val` without freeing an existing value, so it relies on controlled initialization/recycling. `Inactive()` compares against the dummy OSS object. Tests should verify object reuse clears stale flags, path keys remain valid after hide/retire, and callback code respects the documented "handle must be locked" preconditions.
