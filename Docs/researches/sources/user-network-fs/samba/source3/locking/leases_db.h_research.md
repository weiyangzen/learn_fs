<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.h -->
# sources/user-network-fs/samba/source3/locking/leases_db.h

## Purpose
`leases_db.h` declares the lease database interface used by Samba source3 locking and oplock code. It hides the `leases.tdb` record layout while exposing operations for lease-to-file membership, lease state updates, lookup, rename, and file-id copying.

## Important APIs, Types, And Functions
The header forward-declares `struct GUID`, `struct smb2_lease_key`, `struct file_id`, and `struct leases_db_file`. The API includes `leases_db_init`, `leases_db_add`, `leases_db_del`, `leases_db_parse`, `leases_db_rename`, `leases_db_set`, `leases_db_get`, `leases_db_get_current_state`, and `leases_db_copy_file_ids`. `leases_db_parse` exposes a callback over the file array without exposing the containing `leases_db_value`.

## Control Flow
Callers initialize the database in read-only or read/write mode, then address records by client GUID and lease key. Mutators add/remove a specific `file_id`, rename a file entry, or update lease-wide state. Readers either parse all files for a lease, get lease state for a particular file id, or use the sequence-number optimized current-state accessor.

## State And Persistence
The header does not define storage itself; it defines the contract for `leases.tdb` access implemented in `leases_db.c`. The database state is keyed by lease identity and includes both per-lease fields and per-file membership entries.

## Dependencies And Integration Points
It is included by `leases_db.c`, `leases_util.c`, `locking.c`, and share-mode code that manages lease entries during open, close, rename, and stale-reference cleanup. It depends on Samba NTSTATUS and generated lease/file structures supplied by broader source3 include chains.

## Risks And Test Signals
Because the header intentionally hides `struct leases_db_file`, callers can only consume file arrays through callbacks or copy helpers; misuse of callback lifetimes is the main integration risk. Test signals are compile coverage for all users, read-only initialization paths, callback parsing of multi-file leases, and correct behavior when `leases_db_get_current_state` reports an unchanged database sequence number.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.h -->
