# sources/storage-engines/sqlite/tool/showdb.c

## Purpose

Comprehensive SQLite database-file inspection tool. It can dump raw pages, decode database headers, decode b-tree pages and individual cells, inspect freelist trunks, report page usage for every page, and inspect pointer-map coverage.

## Important APIs, control flow, and dependencies

Global `g` stores page geometry, file handles, output options, page-use annotations, and optional timestamp VFS tags. `fileOpen()`, `fileRead()`, `fileGetsize()`, and `fileClose()` abstract reads either through SQLite's VFS file pointer (`SQLITE_FCNTL_FILE_POINTER`) or raw OS APIs with `--raw`. Header and byte output are handled by `print_byte_range()`, `print_page()`, `print_decode_line()`, and `print_db_header()`. B-tree decoding uses `decodeVarint()`, `decodeInt32()`, `localPayload()`, `describeContent()`, `describeCell()`, `decodeCell()`, and `decode_btree_page()`. Freelist and whole-file usage reporting use `decode_trunk_page()`, `page_usage_msg()`, `page_usage_cell()`, `page_usage_btree()`, `page_usage_freelist()`, `page_usage_ptrmap()`, `page_usage_report()`, and `ptrmap_coverage_report()`. `main()` parses switches (`--raw`, `--csv`, `--tmstmp`) and commands including `dbheader`, `pgidx`, `ptrmap`, page ranges, `NNNb*`, and `NNNt*`.

## State, persistence, and integration

The program is read-only, but by default reads via SQLite's VFS so URI filenames and VFS-specific behavior can be honored. It opens a separate SQLite connection during `pgidx` to query `SQLITE_MASTER`, enables `PRAGMA writable_schema=ON`, and then recursively marks b-tree, overflow, freelist, and pointer-map pages. It understands page-1's 100-byte database header, reserved bytes, autovacuum pointer-map pages, and optional 16-byte `tmstmpvfs` tags stored in reserved space.

## Risks and test signals

Risks are mostly parser robustness and stale file-format assumptions: malformed cell offsets can cause confusing output or bounds errors, page usage is heuristic for corrupt pages, and CSV fields are derived from human-readable messages. The default VFS path can observe SQLite-level file views that differ from raw bytes. Test signals include decoding known fixture databases, `pgidx` coverage with no duplicate or out-of-range page errors, `ptrmap` agreement on autovacuum databases, b-tree cell decode matching SQL content, and both raw and VFS read modes.
