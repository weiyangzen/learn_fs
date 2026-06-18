# sources/user-network-fs/samba/source3/lib/xattr_tdb.c

## Purpose
`xattr_tdb.c` emulates POSIX extended attributes by storing NDR-encoded xattr arrays in a TDB/dbwrap database keyed by Samba file IDs.

## Important APIs and Functions
Public operations are `xattr_tdb_getattr`, `xattr_tdb_setattr`, `xattr_tdb_listattr`, `xattr_tdb_removeattr`, and `xattr_tdb_remove_all_attrs`. Internal helpers marshal/unmarshal `struct tdb_xattrs` (`xattr_tdb_pull_attrs`, `xattr_tdb_push_attrs`), fetch records (`xattr_tdb_load_attrs`), lock records (`xattr_tdb_lock_attrs`), and save records (`xattr_tdb_save_attrs`).

## Control Flow and Persistence
File IDs are reduced to a 16-byte dev/inode-compatible key via `push_file_id_16` for backward compatibility. Reads fetch and decode a record, scan for the named EA, steal the value blob to caller memory, and set `ENOATTR` when absent. Sets fetch-lock the record, decode existing attributes, enforce `XATTR_CREATE` and `XATTR_REPLACE`, grow the EA array if needed, point the EA name/value at caller data, marshal, and store. Listing first calculates the required null-separated name-list length, checks buffer size, then copies names. Remove swaps the target entry with the last entry and either saves or deletes the record. Remove-all deletes the locked record.

## Dependencies and Integration Points
It depends on dbwrap, TDB data helpers, NDR generated xattr/file_id types, `file_id` utilities, errno conventions, and `XATTR_*` flags. It integrates with VFS modules that need xattr behavior on filesystems lacking native xattrs or for Samba-specific metadata.

## Risks and Edge Cases
Backward-compatible 16-byte file IDs can alias if newer file ID components matter. `xattr_tdb_setattr` stores pointers to caller `name` and `value` in the temporary structure before immediate marshal; this is safe only because save happens before those pointers go out of scope. On decode failure, some error paths return `-1` without setting a precise errno. `listattr` returns the required size with `errno=ERANGE`, matching xattr conventions. Tests should cover create/replace flags, missing records, corrupt NDR blobs, empty EA sets deleting records, list buffer sizing, value ownership after get, and remove-all idempotence.
