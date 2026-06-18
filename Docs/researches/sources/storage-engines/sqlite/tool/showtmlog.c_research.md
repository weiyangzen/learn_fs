# sources/storage-engines/sqlite/tool/showtmlog.c

## Purpose

Decoder for 16-byte `tmstmpvfs` log records. It renders page and WAL activity either as human-readable text or as CSV.

## Important APIs, control flow, and dependencies

`decodeTimestamp()` converts the six-byte big-endian millisecond timestamp field to `YYYY-MM-DD HH:MM:SS.SSS`, treating zero and far-future values specially. `renderCSV()` and `renderText()` decode record type, transaction flag, page number, frame number, pid, salt, and checkpoint events. Recognized opcodes include open-db, open-wal, wal-page, db-page, checkpoint start/page/end, wal-reset, close-wal, and close-db. `main()` parses `--csv`, `--help`, and one or more log filenames, prints a CSV header when requested, and reads complete 16-byte records until EOF.

## State, persistence, and integration

The tool reads log files only. It is coupled to the binary record layout emitted by SQLite's timestamp VFS extension and can label multiple input files with a sequential file number in CSV output. It shares timestamp decoding logic with `showdb.c`'s optional timestamp page-tag reporting.

## Risks and test signals

Risks include silent ignore of trailing partial records, CSV output that does not escape filenames because filenames are not included, and layout drift with future VFS log versions. Test signals include synthetic records for each opcode, CSV/text parity for the same file, bad-date handling, multi-file numbering, and comparison with observed WAL/page events.
