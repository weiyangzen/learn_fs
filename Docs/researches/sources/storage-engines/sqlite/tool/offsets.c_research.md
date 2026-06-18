# sources/storage-engines/sqlite/tool/offsets.c

## Purpose

Diagnostic utility that locates TEXT or BLOB payload offsets for one column of one table in an SQLite database file. It prints each rowid, field size, and absolute file offset for the requested column, making it useful for low-level storage inspection and corruption/debug work.

## Important APIs, control flow, and dependencies

`GState` holds the current database file, page size, target root page, target column number, a page stack, and an error string. `ofstRootAndColumn()` opens the database through SQLite, queries `sqlite_schema`, `PRAGMA table_info`, and `PRAGMA page_size`, then the rest of the code reads the file directly with stdio. `ofstPushPage()` and `ofstPopPage()` manage recursive page traversal. `ofst2byte()`, `ofst4byte()`, `ofstVarint()`, `ofstSerialSize()`, and `ofstInFile()` decode SQLite b-tree record structures. `ofstWalkInteriorPage()` follows child pages, `ofstWalkLeafPage()` decodes table leaf cells and serial types, and `main()` optionally enables `--trace` before walking the root page.

## State, persistence, and integration

The tool is read-only. It uses SQLite APIs only for schema discovery and then trusts raw on-disk b-tree layout. It handles table b-tree page types 5 and 13, uses a fixed page stack depth of 20, and explicitly skips rows whose payload overflows by printing an overflow comment instead of following overflow pages. It assumes the requested table has rowid-table leaf records shaped like standard table b-tree cells.

## Risks and test signals

Risks include malformed pages causing out-of-bounds reads, deeply nested b-trees exceeding the stack, overflow columns being unreported, and schema/file races between SQLite schema reads and raw file traversal. Test signals are known databases with fixed page sizes and predictable text/blob offsets, `--trace` output matching page metadata, behavior on overflow payloads, and comparison against `dbstat` or independent page decoders.
