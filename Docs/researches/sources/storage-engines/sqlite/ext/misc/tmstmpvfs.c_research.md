# sources/storage-engines/sqlite/ext/misc/tmstmpvfs.c

## Purpose
Implements `tmstmpvfs`, a VFS shim that records page timestamps in the 16-byte reserved region of database pages and optionally emits per-connection binary event logs.

## Important APIs, Types, And Functions
Primary types are `TmstmpFile` and `TmstmpLog`. VFS methods include `tmstmpOpen` and pass-through wrappers for delete/access/path/dlopen/randomness/time/system-call APIs. I/O methods include `tmstmpRead`, `tmstmpWrite`, `tmstmpFileControl`, shared-memory wrappers, fetch/unfetch wrappers, and `tmstmpClose`. Registration is through `tmstmpRegisterVfs()`, `sqlite3_tmstmpvfs_init()`, and static-link helpers `sqlite3_register_tmstmpvfs()`/`sqlite3_unregister_tmstmpvfs()`.

## Control Flow
Loading registers `tmstmpvfs` as the default VFS above the previous default. `xOpen` wraps main database and WAL files; other files bypass the shim. Database opens allocate a `TmstmpLog` and log filename under `<database>-tmstmp/`; WAL opens find the partner DB file through `sqlite3_database_file_object()`. `xRead` of the database header discovers page size and whether reserved bytes equal 16. `xWrite` observes WAL frame headers, WAL resets, checkpoint writes, and rollback-mode DB writes. It timestamps database page reserved bytes only when reserve size is exactly 16 and logs open/write/checkpoint/close events when a log can be opened.

## State And Persistence Behavior
The VFS persists timestamp metadata in each database page's reserved bytes. WAL frames are not modified, preserving WAL checksums; timestamps are applied when frames are checkpointed into the database or when rollback-mode writes update the database file. Logs are external binary files created lazily only if the `<database>-tmstmp` directory exists and a write event needs flushing. Runtime state tracks page size, WAL salt, frame number, checkpoint mode, partner DB/WAL handles, and buffered log records.

## Dependencies And Integration Points
Depends on SQLite VFS and I/O method contracts, file-control operations `SQLITE_FCNTL_VFSNAME`, `SQLITE_FCNTL_CKPT_START`, and `SQLITE_FCNTL_CKPT_DONE`, process ID APIs, stdio logging, `sqlite3_randomness()`, and `sqlite3_database_file_object()`.

## Risks And Edge Cases
`tmstmpWrite()` casts SQLite's write buffer to mutable bytes to fill reserved space before forwarding to the underlying VFS. The shim assumes page writes include the reserved tail and that checkpoint file-control calls bracket checkpoint writes. Logging silently disables itself if the log file cannot be opened. Partner linkage only works for WAL opens associated with a wrapped DB handle. Device characteristics clear `SQLITE_IOCAP_SUBPAGE_READ`, which can affect upper-layer assumptions.

## Test Signals
Tests should create a database with `SQLITE_FCNTL_RESERVE_BYTES=16`, perform rollback and WAL writes, checkpoint WAL frames, inspect reserved bytes for timestamp/frame/salt/flag fields, verify VFS name includes `tmstmp`, verify log records when `<db>-tmstmp` exists, and confirm ordinary reserve=0 databases remain functionally unchanged.
