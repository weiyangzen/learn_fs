# sources/storage-engines/sqlite/tool/showshm.c

## Purpose

Decoder for SQLite WAL-index shared-memory (`-shm`) files. It prints the two `WalIndexHdr` copies and the `WalCkptInfo` checkpoint/read-mark area from the beginning of the shm file.

## Important APIs, control flow, and dependencies

`getContent()` reads bytes from the opened file descriptor. `print_decode_line()` displays fields as big-endian, native-byte-order, hex, or page-size values using `FG_HEX`, `FG_NBO`, and `FG_PGSZ`. `print_index_hdr()` decodes each 48-byte wal-index header copy, including version, transaction counter, initialization flag, checksum byte order, page size, mxFrame, database page count, frame checksum, salts, and header checksum. `print_ckpt_info()` decodes `nBackfill`, five read marks, lock bytes, `nBackfillAttempted`, and padding. `main()` reads the first 136 bytes and prints all structures.

## State, persistence, and integration

The program is read-only and uses OS file APIs. It assumes the shm file begins with SQLite's wal-index layout and interprets some fields in native byte order because the wal-index is host-local shared memory, not a portable database file format. It does not inspect hash tables or later shm regions.

## Risks and test signals

Risks include native-endian interpretation on a file copied between architectures, short reads not checked, and version/layout drift if SQLite changes wal-index internals. Test signals include live WAL databases with known frame counts, consistency between header copies, read-mark values matching active readers/checkpoints, and comparison against WAL header salts/checksums.
