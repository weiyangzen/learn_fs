# sources/storage-engines/sqlite/ext/misc/cksumvfs.c

## Purpose
`cksumvfs.c` implements the `cksmvfs` VFS shim, which stores and verifies an 8-byte checksum in each database page's reserved bytes. It also registers a SQL helper `verify_checksum(BLOB)` and a `checksum_verification` pragma handled through file-control.

## Important APIs, types, and functions
- `CksmFile` extends `sqlite3_file` with original filename, `computeCksm`, `verifyCksm`, and partner linkage fields.
- `cksmCompute()` computes the page checksum over all but the final 8 bytes using SQLite-style pairwise 32-bit accumulation with endian handling.
- `cksmVerifyFunc()` verifies a page-sized BLOB and returns 1, 0, or NULL.
- `cksmRead()` detects reserve-byte setting from page 1, updates flags, and returns `SQLITE_IOERR_DATA` on checksum mismatch when verification is enabled.
- `cksmWrite()` updates flags from page 1 and writes checksum bytes for page-sized writes when enabled.
- `cksmFileControl()` implements `PRAGMA checksum_verification` and blocks `PRAGMA page_size` changes on checksum databases.
- `cksmFetch()` disables memory-mapped fetch for checksum databases so page verification is not bypassed.
- `cksmRegisterVfs()`, static registration helpers, and `sqlite3_cksumvfs_init()` install the VFS as default and auto-register SQL functions.

## Control flow
Loading dynamically registers `verify_checksum()` on the current connection, then registers `cksmvfs` as the default VFS and arranges auto-extension registration for future connections. Main database opens are wrapped; non-main files pass through. Reads and writes of page 1 inspect byte 20 for exactly 8 reserved bytes, toggling checksum computation/verification. Page-sized reads compute and compare checksums; page-sized writes update the final 8 bytes before delegating to the underlying VFS.

## State and persistence behavior
Persistent state is the checksum stored in each page's final 8 reserved bytes and the database header reserve-byte value. Runtime state lives in each `CksmFile`. Verification can be disabled per connection/file via the pragma, but checksum writes continue when compute is enabled.

## Dependencies and integration points
It depends on SQLite 3.32+ for `sqlite3_database_file_object()` per comments, VFS APIs, auto-extension APIs, file-control pragmas, and optional static-link entry points. It forwards most VFS operations to the prior default VFS and decorates `SQLITE_FCNTL_VFSNAME` with `cksm/...`.

## Risks and edge cases
- Checksumming only works when reserved bytes equal exactly 8 and conflicts with other extensions using reserved bytes.
- The checksum write path casts away const and writes into `zBuf`; callers must provide mutable page buffers as SQLite normally does.
- Memory-mapped reads are disabled for checksum databases, which can affect performance.
- Partner fields are maintained on close and flag changes, but this file does not visibly establish partners in `cksmOpen()`; WAL/main coordination may rely on omitted or future code paths.
- Disabling verification enables forensic reads but can hide corruption from normal query paths.

## Test signals
Useful tests include enabling reserve bytes and vacuuming, verifying `verify_checksum(data)` over `sqlite_dbpage`, corrupting page bytes to trigger `SQLITE_IOERR_DATA`, toggling `PRAGMA checksum_verification`, checking that page size changes are blocked, and confirming ordinary reserve-byte-0 databases pass through.
