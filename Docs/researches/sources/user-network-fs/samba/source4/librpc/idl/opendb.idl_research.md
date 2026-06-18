# sources/user-network-fs/samba/source4/librpc/idl/opendb.idl

## Purpose

`opendb.idl` defines NDR-serializable records for Samba's open-file database, used by `ntvfs/common/opendb.c` to store open handles, sharing state, delete-on-close state, oplock state, and pending notifications.

## Important APIs And Types

The interface imports `server_id.idl`. `opendb_entry` records the owning server id, stream id, share access, access mask, opaque file handle and file descriptor pointers, per-entry delete-on-close, level-II oplock allowance, and oplock level. `opendb_pending` records a server id and notification pointer. Public `opendb_file` stores per-path state: delete-on-close, write timestamps, UTF-8 path, entry count and array, pending count and array.

## Control Flow And State

The file is schema only, but it models persistent/shared database state. The database can be loaded by multiple server processes to enforce share modes and track pending open operations. Counts drive variable-length arrays in generated parsers.

## Dependencies And Integration Points

Generated NDR code is consumed by open database code in the NTVFS layer. It depends on server-id serialization and Samba's representation of `NTTIME`, `utf8string`, pointer values, and boolean8 fields.

## Risks

Pointer fields are serialized as opaque identifiers and are process-context-sensitive; misuse across process boundaries can be unsafe unless the owning code treats them as tokens. Count/array consistency is critical. Incorrect delete-on-close or oplock state persistence can cause data-loss or sharing-mode regressions.

## Test Signals

Round-trip tests should serialize open files with multiple entries and pending records. Integration tests should exercise conflicting opens, delete-on-close on one handle versus per-file state, oplock state, and database reload after process handoff.
