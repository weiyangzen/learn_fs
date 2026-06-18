# sources/storage-engines/sqlite/src/dbstat.c

## Purpose

`dbstat.c` implements the optional `dbstat` virtual table used by `sqlite3_analyzer` and diagnostics to report B-tree page layout, payload, unused bytes, page paths, overflow chains, offsets, and aggregate space usage by table or index.

## Important APIs, Types, and Functions

- `zDbstatSchema` declares visible columns (`name`, `path`, `pageno`, `pagetype`, `ncell`, `payload`, `unused`, `mx_payload`, `pgoffset`, `pgsize`) plus hidden `schema` and `aggregate`.
- `StatCell` records per-cell local payload, child page, overflow pages, last overflow payload, and overflow iteration state.
- `StatPage` owns a copied page buffer, path string, decoded flags, cells, right-child page, unused bytes, and max payload.
- `StatCursor` owns the root-page statement, traversal stack, aggregate flag, output fields, and running counters.
- `statBestIndex()` recognizes `schema=`, `name=`, `aggregate=`, and ordered output by `(name,path)`.
- `statFilter()` builds a query over `sqlite_schema` plus the schema table root and initializes traversal.
- `statGetPage()` copies pager page data into a padded buffer.
- `statDecodePage()` parses B-tree headers, cells, freeblocks, local payload, and overflow chains.
- `statNext()` performs depth-first traversal and emits either each page/overflow page or one aggregate row per B-tree.
- `sqlite3DbstatRegister()` registers `"dbstat"`.

## Control Flow and Behavior

The module starts from a prepared statement that lists root pages: `sqlite_schema` page 1 plus every schema object with a nonzero rootpage. Optional `name=` filters this list, and optional `schema=` chooses an attached database. The cursor uses `aPage[32]` as a traversal stack. For non-aggregate scans, each B-tree page and overflow page becomes a row with a path string. For aggregate scans, `statNext()` keeps walking until the current B-tree is exhausted, accumulating counts into one row.

`statDecodePage()` copies the page image before decoding and adds 256 bytes of padding to tolerate limited overreads on corrupt data, matching pager/B-tree safety assumptions. It decodes table/index leaf/internal flags, cell pointer arrays, freeblock chains, right-child pointers, varint payload sizes, rowids for table leaves, local payload sizes, and overflow page chains by following pager pages. If page structure is corrupt, it clears cells, sets flags to zero, and later reports `pagetype='corrupted'`.

Overflow rows are emitted before descending into the child page associated with the cell, matching the documented binary path ordering. `statSizeAndOffset()` usually computes offset as `(pageno-1)*page_size`, but asks ZIPVFS via file-control opcode `230440` for compressed page size/offset when available.

## State and Persistence

The module is read-only. It allocates and frees page buffers, cell arrays, overflow arrays, path strings, and a root-page statement per cursor. It reads pager pages and follows B-tree state as of the current connection snapshot. Aggregate counters accumulate page counts, payload, unused bytes, page size, and max payload.

## Dependencies and Integration Points

This file depends on virtual table APIs, SQLite internal pager/B-tree APIs, schema querying, varint decoding, page-size/reserve-byte APIs, OS file-control for ZIPVFS, memory allocation, and SQLite string formatting. It is direct-only because it exposes low-level file layout. It supports the `sqlite3_analyzer` tool and SQL-level inspection.

## Risks and Edge Cases

Corrupt pages can contain invalid flags, freeblock loops, bad cell offsets, impossible payload sizes, or overflow chains pointing to unreadable pages. The decoder attempts to avoid undefined behavior but may return pager errors when following overflow pages. Traversal depth is limited by `aPage[32]`; deeper structures return `SQLITE_CORRUPT_BKPT`. `statResetCsr()` must clear page allocations before resetting the root statement because OOM can reset pager state. `name=` SQL generation lacks an intervening space before `WHERE` in the appended string, so tests should confirm the generated statement is accepted or catch regressions around this path.

## Test Signals

Tests should cover ordinary rowid and WITHOUT ROWID tables, indexes, overflow payloads, aggregate and non-aggregate modes, attached schema selection, `name=` filtering, order-by consumption, ZIPVFS file-control behavior, corrupted page flags/freeblocks/cell offsets, overflow pager failures, deep B-tree corruption, OOM cleanup, schema page row inclusion, and disabled-module registration stubs.
