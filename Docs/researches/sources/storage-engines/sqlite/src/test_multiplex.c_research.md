# sources/storage-engines/sqlite/src/test_multiplex.c

## Purpose

`test_multiplex.c` implements the `multiplex` VFS shim, splitting one logical SQLite file into numbered chunk files to test large-file behavior and filesystem size-limit scenarios.

## Important APIs, types, and functions

`multiplexGroup` stores chunk handles/names, base filename, flags, chunk size, enabled flag, and truncation mode. `multiplexConn` is the file wrapper. `gMultiplex` stores the original VFS, wrapper VFS, I/O methods, and init flag. Public APIs are `sqlite3_multiplex_initialize()` and `sqlite3_multiplex_shutdown()`. Key routines include filename generation, subfile open/size/close, `multiplexOpen`, `multiplexDelete`, `multiplexRead`, `multiplexWrite`, `multiplexTruncate`, `multiplexFileSize`, and `multiplexFileControl`.

## Control flow

Initialization clones the real VFS, overrides callbacks, registers `multiplex`, and auto-registers SQL `multiplex_control(op,val)`. Open parses URI options, rounds chunk size, adjusts around the pending byte, opens chunk 0, detects existing overflow chunks, and selects I/O method version. Reads/writes split operations across chunk boundaries, truncation removes or zeroes higher chunks, and file-control handles multiplex controls/pragmas.

## State and persistence behavior

Persistent state is the chunk-file set: base filename for chunk 0 and numbered names for later chunks, with special 8.3 offsets for journals and WAL. Runtime group state is per open file and freed on close. Shutdown unregisters the VFS but does not delete database chunks.

## Dependencies and integration points

It depends on SQLite VFS APIs, URI helpers, `sqlite3ext.h`, `test_multiplex.h`, and optionally `sqlite3PendingByte`. Tcl commands expose initialize, shutdown, and control operations. It integrates with pager, WAL, journal, URI, pragma, and large-database tests.

## Risks and test signals

Initialize/shutdown are not thread-safe. Existing chunk-size inference can disable multiplexing if files look inconsistent. Reads may create missing chunks. Max-chunks control is accepted but not enforced. Signals include numbered chunk files, logical size aggregation, boundary-spanning I/O, truncate behavior, multiplex pragmas, and VFS names prefixed with `multiplex/`.
