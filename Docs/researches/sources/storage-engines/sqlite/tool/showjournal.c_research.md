# sources/storage-engines/sqlite/tool/showjournal.c

## Purpose

Rollback-journal decoder that prints journal headers and page records from an SQLite rollback journal file.

## Important APIs, control flow, and dependencies

The global state tracks page size, sector size, file handle, file size, and checksum nonce. `read_content()` reads arbitrary byte ranges with zero-fill on short read. `print_decode_line()` displays big-endian integer fields. `decode_journal_header()` reads a 64-byte header at a sector boundary, prints header magic parts, page count, checksum nonce, initial database size, sector size, and page size, and updates global page/sector parameters. `print_page()` prints the page number field for a journal page record. `main()` walks the file by sectors and records until EOF.

## State, persistence, and integration

The tool is read-only and depends only on stdio. It tracks the page and sector sizes from each decoded journal header and uses them to advance through page records. If the header page count is zero, it estimates record count from file size. It does not validate page checksums or restore database pages.

## Risks and test signals

Risks include incomplete checksum coverage, simplistic handling of malformed headers, integer-sized file offsets, and confusing output if sector/page sizes are corrupt. Test signals include journals produced by controlled transactions, matching page numbers and header metadata from SQLite's journal format, behavior with zero page-count journals, and short-read diagnostics on truncated files.
