# sources/user-network-fs/samba/source4/ntvfs/common/opendb.h

## Purpose

`opendb.h` defines the backend operations interface for the NTVFS open-file database and the small structure used to notify clients about oplock breaks.

## Important APIs, Types, and Functions

The central type is `struct opendb_ops`, with function pointers for init, lock, key retrieval, open registration, pending-open registration/removal, close, rename, path lookup, delete-on-close, write time, file info lookup, share-mode checks, oplock update, and oplock breaks. `struct opendb_oplock_break` contains a file handle pointer and break level. It declares `odb_set_ops()` and `odb_tdb_init_ops()`.

## Control Flow

The header defines the dispatch contract implemented by `opendb_tdb.c` and called by `opendb.c`. There is no executable flow.

## State and Persistence Behavior

Backend state is abstracted through opaque `struct odb_context` and `struct odb_lock` pointers. The interface models persistent runtime open-file records and caller-held DB locks.

## Dependencies and Integration Points

It is included by `ntvfs_common.h` and depends on NTVFS, NT time, oplock, and access-mask types through existing includes. Messaging handlers use `opendb_oplock_break` payloads for `MSG_NTVFS_OPLOCK_BREAK`.

## Risks and Edge Cases

Function pointer signatures must remain consistent with wrapper and backend implementations. `void *file_handle` and `void *private_data` are process-local identifiers sent through persistent records or messages, so lifetime and server identity checks are critical.

## Test Signals

Compile-time coverage should catch signature drift. Runtime tests should verify oplock-break payload interpretation and all operations through the wrapper/backend path.
