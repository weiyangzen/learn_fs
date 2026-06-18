# sources/storage-engines/sqlite/tool/showstat4.c

## Purpose

Utility that queries and decodes the `sqlite_stat4` table in a database, printing each index sample as raw hex and as decoded record values.

## Important APIs, control flow, and dependencies

`decodeVarint()` decodes SQLite varints from stat4 sample records. `main()` opens the database with SQLite, prepares `SELECT tbl||'.'||idx, nEq, nLT, nDLt, sample FROM sqlite_stat4 ORDER BY 1`, groups output by table/index, prints cardinality strings, hex-dumps the sample blob, then decodes the record header serial types and payload fields. It handles NULL, integer serial types, floating point, zero/one constants, blobs, and printable/escaped text.

## State, persistence, and integration

The utility is read-only and depends on the database already having `sqlite_stat4` rows, typically from `ANALYZE` with STAT4 support. Its binary record decoding mirrors SQLite record serial-type rules, but only for display. It does not alter planner statistics.

## Risks and test signals

Risks include malformed sample blobs, missing `sqlite_stat4`, byte-order subtleties for double printing, and text escaping that is diagnostic rather than full SQL literal reconstruction. Test signals include databases with known ANALYZE output, samples covering all serial types, graceful error display for corrupt blobs, and output grouped by `tbl.idx`.
