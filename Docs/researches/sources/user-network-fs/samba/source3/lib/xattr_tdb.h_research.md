# sources/user-network-fs/samba/source3/lib/xattr_tdb.h

## Purpose
This header declares the TDB-backed xattr emulation API.

## Important APIs and Types
It includes generated `file_id` definitions and declares get, set, list, remove, and remove-all functions operating on `struct db_context`, `struct file_id`, and `DATA_BLOB`.

## Dependencies and Integration Points
It is consumed by VFS or metadata modules that already know their dbwrap database and file IDs. It keeps database creation/opening outside the helper API.

## Risks and Test Signals
The header lacks include guards in the viewed content, so repeated inclusion relies on surrounding headers or compiler tolerance. Compile tests should include it multiple times in a translation unit and verify declarations match `xattr_tdb.c`.
