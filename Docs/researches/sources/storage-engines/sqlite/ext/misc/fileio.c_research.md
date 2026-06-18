# sources/storage-engines/sqlite/ext/misc/fileio.c

## Purpose

`fileio.c` implements filesystem-facing SQL helpers: `readfile()`, `writefile()`, `lsmode()`, `realpath()`, and eponymous virtual table `fsdir`. These functions support CLI import/export and archive workflows that need to read, write, or enumerate files from SQL.

## Important APIs, types, and functions

`sqlite3_fileio_init()` registers direct-only `readfile` and `writefile`, `lsmode`, `realpath`, and the `fsdir` module. `readFileContents()` reads a whole file into a SQLite blob with length-limit checks. `writeFile()` handles regular files, directories, symlinks on Unix, chmod, and optional mtime. `makeDirectory()` creates missing parent directories. `lsModeFunc()` formats POSIX mode bits.

For `fsdir`, `fsdir_cursor` tracks recursion levels, base path, current stat, current path, and rowid. `FsdirLevel` owns an open `DIR*` plus directory path. The virtual table schema is `(name,mode,mtime,data,level,path HIDDEN,dir HIDDEN)`. Platform helpers provide UTF-8 path support and time conversion on Windows. `portable_realpath()` and `realpathFunc()` resolve existing path prefixes and append missing tails.

## Control flow

`readfileFunc()` returns NULL for NULL or unreadable paths, otherwise delegates to `readFileContents()`. `writefileFunc()` parses 2 to 4 arguments, mode, and mtime, calls `writeFile()`, creates parent directories on `ENOENT`, and raises detailed errors when mode was supplied and writing still fails. `writeFile()` chooses symlink, directory, or regular-file behavior from `mode`; regular files return bytes written.

`fsdirBestIndex()` requires `path=` and optionally accepts `dir=` and `level` constraints, rejecting plans with unusable input constraints. `fsdirFilter()` builds the starting path, stats it, and positions the first row. `fsdirNext()` emits the current path first, then descends into directories depth-first, skipping `.` and `..`, statting each child with `lstat` on Unix. `fsdirColumn()` returns names relative to `dir` when supplied, stat metadata, file data blobs, symlink targets, or NULL for directory data.

## State and persistence

`readfile`, `fsdir`, and `realpath` read filesystem state. `writefile` mutates filesystem state by creating or replacing files, directories, symlinks, permissions, and timestamps. The SQLite database is not modified by the module itself. `fsdir` cursor state owns open directory handles and closes them during reset/close.

## Dependencies and integration points

It depends on C stdio, POSIX or Windows filesystem APIs, SQLite direct-only function registration, virtual tables, and optionally `sqlite3_stdio.h` when compiled into the CLI. `fsdir` is marked `SQLITE_VTAB_DIRECTONLY` because it exposes filesystem contents.

## Risks

This is a high-trust extension because it reads and writes arbitrary paths available to the process. Direct-only flags on `readfile`, `writefile`, and `fsdir` are important security boundaries. Whole-file reads can be expensive and are bounded only by SQLite length limit and memory. Recursive `fsdir` can traverse large trees and follows directory structure without cycle detection beyond not descending into symlinked directories on Unix because it uses `lstat`. `realpathFunc()` documents a FIXME where OOM may return NULL instead of an explicit error. Cross-platform differences exist for symlinks, chmod, stat timestamps, and path separators.

## Test signals

Tests should cover file reads, unreadable/missing files returning NULL, blob length limit errors, writing regular files, parent directory creation, chmod and mtime, directory and symlink modes, write errors with and without mode arguments, `lsmode` formatting, `fsdir` recursion, level limits, relative `dir` behavior, symlink data, direct-only restrictions, Windows UTF-8 path behavior where available, and `realpath` for existing and not-yet-existing paths.
