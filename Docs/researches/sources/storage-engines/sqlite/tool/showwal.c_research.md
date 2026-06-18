# sources/storage-engines/sqlite/tool/showwal.c

## Purpose

SQLite WAL-file inspection utility. It prints WAL headers, summarizes frames with checksum verification, dumps full frame content, decodes frame payload pages as b-trees, and can truncate a WAL after a specified frame on non-MSVC builds.

## Important APIs, control flow, and dependencies

Global state tracks WAL page size, file descriptor, frame count, and hex formatting. `Cksum`, `getInt32()`, `swab32()`, and `extendCksum()` implement SQLite WAL checksum accumulation with byte-order detection. `getContent()`, `print_byte_range()`, `print_decode_line()`, `print_wal_header()`, `print_oneline_frame()`, and `print_frame()` handle raw display. The b-tree page decoder reuses local versions of `decodeVarint()`, `localPayload()`, `describeContent()`, `describeCell()`, and `decode_btree_page()`. `main()` reads the page size from WAL header offset 8, computes frame count, and supports `header`, frame ranges, `NNNb*` b-tree decode arguments, and `NNNtruncate`.

## State, persistence, and integration

Most modes are read-only, but the `truncate` suffix intentionally calls `truncate()` to shorten the WAL. The tool depends on the WAL file format: 32-byte header, 24-byte frame headers, salts, commit db-size field, and page payloads. It decodes the frame payload using database b-tree page rules, but page number and frame number are distinct.

## Risks and test signals

Risks include unchecked short reads, host alignment assumptions while checksuming 32-bit words, accidental destructive use of `truncate`, and stale b-tree decode assumptions. Checksum mismatch output is a strong corruption signal, while b-tree decode is diagnostic. Test signals include WALs with known frame counts, valid and intentionally corrupted checksums, page-size boundary cases, frame range dumps, and b-tree frame decoding that matches the database page content.
