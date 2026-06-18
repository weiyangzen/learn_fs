# Research: sources/storage-engines/sqlite/ext/misc/zipfile.c

## Purpose

`zipfile.c` implements SQLite's `zipfile` extension: a virtual table for reading and writing ZIP archives and an aggregate SQL function that builds an archive blob from rows. It exposes archive entries as rows with name, POSIX mode, modification time, uncompressed size, raw compressed data, uncompressed data, compression method, and hidden archive argument/cursor id.

The implementation supports ordinary single-file ZIP archives with classic 32-bit fields and methods 0 (stored) and 8 (deflate). It explicitly does not support encryption, split archives, zip64, or compression methods beyond inflate/deflate.

## Important APIs, Types, And Functions

- `sqlite3_zipfile_init()` registers the module and aggregate through `zipfileRegister`.
- `ZIPFILE_SCHEMA` declares `name PRIMARY KEY, mode, mtime, sz, rawdata, data, method, z HIDDEN` as a WITHOUT ROWID virtual table.
- `ZipfileEOCD`, `ZipfileCDS`, and `ZipfileLFH` model ZIP end-of-central-directory, central-directory, and local-file-header records.
- `ZipfileEntry` stores parsed central-directory metadata, Unix mtime, extra/comment data, compressed data offset or in-memory bytes, and linked-list state.
- `ZipfileTab` stores the archive filename, DB handle, scratch buffer, active cursors, and write-transaction state (`pFirstEntry`, `pWriteFd`, `szCurrent`, `szOrig`).
- `ZipfileCsr` stores file-backed scan state, in-memory scan state, current entry, and cursor id.
- Parsing helpers include `zipfileReadEOCD`, `zipfileReadCDS`, `zipfileReadLFH`, `zipfileGetEntry`, `zipfileScanExtra`, and endian read/write helpers.
- Compression helpers `zipfileInflate` and `zipfileDeflate` use zlib raw deflate streams (`windowBits=-15`).
- Write helpers include `zipfileBegin`, `zipfileUpdate`, `zipfileAppendEntry`, `zipfileSerializeLFH`, `zipfileSerializeCDS`, `zipfileCommit`, and `zipfileRollback`.
- `zipfileStep`/`zipfileFinal` implement the aggregate `zipfile()` builder.
- `zipfileFindFunction` exposes `zipfile_cds(cursor_id)` for rows of this virtual table.

## Control Flow

Connecting validates constructor usage: an eponymous `zipfile` table may be called without a fixed filename, but a differently named virtual table must supply exactly one filename argument. It declares the schema, allocates one table object plus a 200 KiB scratch buffer, dequotes a fixed filename when present, and marks the table `SQLITE_VTAB_DIRECTONLY`.

Planning looks for an equality constraint on hidden column `z`. Eponymous use such as `zipfile($filename)` passes the archive filename/blob as this hidden argument. If a hidden-column constraint is present but unusable, planning returns `SQLITE_CONSTRAINT`.

Filtering resets the cursor, determines whether to read a fixed table filename, a filename argument, or a BLOB containing an entire archive image, then loads or scans the central directory. File-backed scans open the archive read-only, locate EOCD by scanning backward over the last up to 200 KiB, set `iNextOff` to the central directory offset, and parse entries lazily with `zipfileNext`. Blob-backed scans load entries into memory and copy compressed data into each entry.

Column access returns metadata directly, reads raw compressed bytes from the archive when needed, inflates data for `data` when method is 8, returns stored data directly for method 0, and returns SQL NULL for directories. Zero-length non-directories return an empty blob.

Writes begin lazily from `xUpdate` if no write transaction is active. `zipfileBegin` opens the archive `ab+`, records original/current size, and loads the existing central directory into memory. `zipfileUpdate` handles DELETE, INSERT, and UPDATE by removing old list entries, validating `sz`/`rawdata` are NULL for writes, deriving directory status from `data IS NULL`, validating mode, normalizing directory names to end in `/`, choosing/storing compression, writing the new local header and data at the current end, and inserting a new central-directory entry in memory. `zipfileCommit` appends all central-directory records plus EOCD, then cleans transaction state. `zipfileRollback` currently calls `zipfileCommit`, so transaction rollback does not restore the original archive.

The aggregate builder follows the same entry serialization rules but accumulates body and central-directory buffers in memory, then returns a single blob containing body, CDS records, and EOCD.

## State And Persistence Behavior

Read-only scans maintain either an open `FILE *` with lazy current-entry parsing or an in-memory linked list derived from a blob. A fixed-filename virtual table stores `zFile`; eponymous calls pass filename/blob through the hidden column. The hidden `z` output for scanned rows is a cursor id used by `zipfile_cds()`.

Write transactions append new local file headers and data immediately to the archive file, while central-directory state is kept in memory until commit. Existing entries remain physically present in the file when deleted or replaced; they are omitted from the newly appended central directory. This append-only rewrite style can grow archives and depends on readers honoring the last EOCD. `szOrig` is recorded but not used to truncate on rollback, and `xRollback` commits, so SQLite rollback semantics are not durable for archive file side effects.

The aggregate function stores all generated archive bytes in memory until finalization. ZIP timestamps are stored in both DOS date/time fields and a 0x5455 extended timestamp extra field for new entries.

## Dependencies And Integration Points

The file depends on SQLite extension, virtual-table, aggregate-function, memory, VFS time, conflict-policy, and overload-function APIs; zlib for `crc32`, `deflate`, and `inflate`; stdio for file I/O; and optional `sqlite3_stdio.h` remapping for CLI builds. It includes local POSIX mode constants to avoid platform header dependencies.

Integration points are SQL queries against `zipfile(...)`, writable virtual tables created with a fixed archive filename, the `zipfile()` aggregate, `zipfile_cds()` virtual-table function, SQLite conflict policies for duplicate names (`IGNORE`, `REPLACE`, default constraint), and the default VFS clock for write mtimes.

## Risks And Edge Cases

- Zip64, encryption, split archives, and unsupported compression methods are rejected or misread by design.
- File I/O uses `fseek`/`ftell` with casts to `long`, which can limit very large archive support on some platforms.
- EOCD scanning only covers the last 200 KiB, enough for normal comments but still bounded.
- Embedded NULs in filenames are copied safely into allocated buffers, but most later path handling uses C-string functions, so such names remain risky.
- `zipfileRollback()` calls `zipfileCommit()`, so SQL rollback does not undo writes to the archive; this is the most important persistence hazard.
- Deletes/replaces append a new central directory but do not reclaim old file bytes.
- `zipfileGetMode` requires mode/data consistency; callers must use `data NULL` for directories and non-NULL for files/symlinks.
- Duplicate detection ignores trailing `/`, so directory/file naming collisions are treated specially.
- New entries cap filename length at 250 bytes for Windows compatibility.
- `zipfileInflate` assumes the uncompressed size from headers and returns errors if zlib does not end exactly as expected.

## Test Signals

Tests should cover reading file-backed and blob-backed archives, empty archives, central-directory corruption, malformed LFH/CDS signatures, extended timestamps, DOS timestamp fallback, directory entries, zero-length files, stored and deflated entries, unsupported compression methods, `rawdata` vs `data`, and `zipfile_cds()`. Write tests should cover insert/update/delete, duplicate names with default/IGNORE/REPLACE conflict policies, directory slash normalization, mode parsing in numeric and string forms, aggregate construction for 2/4/5 argument forms, large filenames rejection, and the documented rollback/append-only behavior.
