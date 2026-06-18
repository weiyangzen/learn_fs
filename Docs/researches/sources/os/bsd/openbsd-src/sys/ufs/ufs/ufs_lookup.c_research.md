# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_lookup.c

Read completely: 1073 lines.

Implements UFS pathname component lookup and directory entry mutation helpers.

Core behavior:
- `ufs_lookup()` validates directory access, handles read-only mutation rejection, consults the namecache, optionally builds/uses dirhash for large directories, falls back to linear scanning, records found entry metadata, tracks reusable free slots for CREATE/RENAME, and handles `LOOKUP`, `CREATE`, `DELETE`, and `RENAME` namei contracts.
- Lookup carefully handles `.` and `..`, parent locking, sticky directories, negative namecache entries, and the two-pass `i_diroff` optimization.
- `ufs_dirbad()` reports/panics on bad directories for writable filesystems; `ufs_dirbadentry()` validates record size, alignment, name length, and null termination.
- `ufs_makedirentry()` fills `struct direct` for a target inode and component name.
- `ufs_direnter()` writes new directory entries, either extending the directory with a fresh block or compacting existing free space, updates dirhash state, writes buffers synchronously, updates timestamps, and truncates trailing unused directory blocks when possible.
- `ufs_dirremove()` removes entries by zeroing first-in-block entries or merging record length into the previous entry; it decrements target link counts.
- `ufs_dirrewrite()` rewrites an existing entry to a new inode/type and decrements the old inode link count.
- `ufs_dirempty()` verifies only `.` and `..` remain; `ufs_checkpath()` walks `..` links to prevent moving a directory into its own subtree.

Integration and risks:
- Directory mutation depends on lookup-populated inode side effects (`i_offset`, `i_count`, `i_reclen`, `i_endoff`).
- Parent/child vnode lock ordering is central to avoiding deadlocks and rename races.
- Dirhash updates must mirror every entry move/remove/add.
- Corrupt directory records can panic on writable filesystems.
