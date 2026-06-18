# sources/storage-engines/sqlite/ext/misc/appendvfs.c

## Purpose
`appendvfs.c` implements the `apndvfs` VFS shim, allowing an SQLite database to be appended to another file such as an executable. It exposes only the database segment to SQLite while the underlying VFS sees the full file.

## Important APIs, types, and functions
- `ApndFile` extends `sqlite3_file` with `iPgOne` (database start offset) and `iMark` (append-marker offset).
- `apnd_io_methods` translates file operations by adding `iPgOne` to database offsets.
- Marker helpers `apndWriteMark()`, `apndReadMark()`, `apndIsAppendvfsDatabase()`, and `apndIsOrdinaryDatabaseFile()` detect and maintain the `Start-Of-SQLite3-` trailer with an 8-byte big-endian offset.
- `apndOpen()` implements the decision rules for ordinary DBs, existing appended DBs, creating appended DBs, and rejecting unrecognized files.
- `sqlite3_appendvfs_init()` registers `apndvfs` over the current default VFS.

## Control flow
For main database files, `apndOpen()` opens the base file, measures it, and applies ordered detection rules: empty/ordinary databases pass through, existing appendvfs files are exposed from the trailer offset, and unknown files opened with `SQLITE_OPEN_CREATE` get a rounded-up future `iPgOne`. Reads add `iPgOne`; writes ensure the append marker exists or is moved before writing content; truncation writes a new marker first, then truncates the underlying full file after the marker.

## State and persistence behavior
Persistent state is the trailer marker appended to the host file and any padding between the prefix and database. In-memory state is per-open `ApndFile`. Ordinary SQLite database files are handled as pass-through by copying the base file object/method dispatch.

## Dependencies and integration points
It depends on SQLite VFS APIs, extension initialization, and the underlying default VFS. It forwards locking, shared-memory, randomness, time, dynamic-loading, access, delete, and syscall methods to the original VFS. `SQLITE_FCNTL_VFSNAME` is decorated with `apnd(offset)/...`.

## Risks and edge cases
- The combined file size is limited to less than `0x40000000` to avoid Windows pending-byte complications.
- Shared-memory and WAL operations are passed through to the underlying full file name, so operational behavior should be tested with journaling modes.
- If marker writes or truncate operations fail, the file can be left with old content/marker combinations; the code writes the marker before truncating to reduce data loss.
- Opening an unrecognized non-SQLite file without create fails with `SQLITE_CANTOPEN`.

## Test signals
Useful tests include opening ordinary databases through `apndvfs`, creating a database appended to a non-database prefix, reopening it via marker detection, verifying `xFileSize()` reports only the database segment, writing/truncating pages, and checking `SQLITE_FCNTL_VFSNAME`.
