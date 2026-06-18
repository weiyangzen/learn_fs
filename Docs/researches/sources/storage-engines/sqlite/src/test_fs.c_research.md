# sources/storage-engines/sqlite/src/test_fs.c

## Purpose

`test_fs.c` exposes host filesystem data to SQLite tests through read-only virtual tables: `fs` maps rows in an index table to file contents, `fsdir` lists directory entries for a constrained directory, and `fstree` recursively walks paths and exposes path, size, and data.

## Important APIs, types, and functions

`fs_vtab`/`fs_cursor` hold the index table, database handle, statement, and read buffer. `FsdirCsr` holds an opened `DIR *`, current `dirent`, and rowid. `FstreeCsr` holds a recursive CTE statement and current file descriptor. Key callbacks are the `fs*`, `fsdir*`, and `fstree*` virtual table method families plus Tcl command `register_fs_module`.

## Control flow

`register_fs_module DB` registers all modules on a Tcl database handle. `fs` scans or rowid-seeks the index table, then opens the mapped path to return file data. `fsdir` requires `dir = ?`, opens the directory, and advances with `readdir()`. `fstree` accepts `path` equality/LIKE/GLOB constraints, derives a prefix, and runs a recursive CTE over `fsdir`.

## State and persistence behavior

No database state is persisted beyond virtual table declarations. Cursor state owns prepared statements, buffers, directory handles, and file descriptors. Results reflect the live filesystem at query time.

## Dependencies and integration points

It depends on SQLite virtual table APIs, Tcl, POSIX file/directory APIs, and `windirent` on Windows. It supports Tcl tests needing SQL-visible file fixtures, recursive discovery, or direct file-content probes.

## Risks and test signals

Queries can read arbitrary host files selected by tests. The `fstree` data column appears to allocate/read using `st_mode` where file size is intended, a notable test-code risk. Signals include expected `xBestIndex` costs, empty inaccessible directories, path/name rows, and file-content reads or `SQLITE_IOERR` failures.
