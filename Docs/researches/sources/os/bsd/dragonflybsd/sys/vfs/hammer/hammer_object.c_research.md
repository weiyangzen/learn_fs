# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_object.c

## Purpose
Manages HAMMER object records: in-memory frontend records, merged in-memory/on-disk lookup and iteration, backend record flushing, range deletion, generic media record creation, and B-tree record deletion.

## Key Elements
- Builds an inode-local red-black tree of pending memory records with comparison functions for exact lookup, range scan, overlap detection, and truncation.
- Allocates, references, waits on, releases, and destroys `hammer_record` objects, including target inode dependency handling and reservation cleanup.
- Implements frontend operations for directory entry add/delete, generic record add, bulk data reservation, bulk replacement, and frontend truncation.
- Uses flags such as `DELETED_FE`, `DELETED_BE`, `COMMITTED`, `INTERLOCK_BE`, and cursor delete visibility to distinguish frontend and backend views.
- `hammer_ip_sync_record_cursor()` flushes memory records to media, deletes overwritten ranges, allocates/copies data, inserts B-tree leaves, handles direct-write completion, and converts certain directory-add records into covering deletes.
- `hammer_ip_lookup()`, `hammer_ip_first()`, and `hammer_ip_next()` merge in-memory records with on-disk B-tree records while handling generation changes and duplicate/overwrite cases.
- `hammer_ip_resolve_data()` resolves data from either memory, direct-write-backed reserved media, or on-disk B-tree data.
- Backend deletion helpers delete ranges, auxiliary clean records, individual records, and generic records with restart handling for `EDEADLK`.
- `hammer_create_at_cursor()` writes generic records directly to media for mirroring/snapshot/config paths, verifying CRC for user mirror data or generating CRC for system data.
- `hammer_delete_at_cursor()` adjusts delete TIDs, optionally destroys B-tree elements/data, updates inode counts and `vol0_next_tid`, and propagates mirror TID changes.
- Directory-empty checking scans merged records; mirror localization fixes directory entry payload localization and recalculates CRC.

## Dependencies
Depends heavily on HAMMER cursor, B-tree, inode, flusher, blockmap allocation/reservation, CRC, direct I/O wait, volume accounting, and transaction/sync-lock APIs.

## Behavior/Risks
This file encodes core consistency rules between frontend-visible pending records and backend media state. It contains explicit unimplemented edge cases for unaligned range deletion and panics on left/right truncation edge cases. Correctness depends on cursor flags, record generation reseeks, direct-I/O waits before commit/destruction, and avoiding duplicate visibility between memory records and B-tree records.
