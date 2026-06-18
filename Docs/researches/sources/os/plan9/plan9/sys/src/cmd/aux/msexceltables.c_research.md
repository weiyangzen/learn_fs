# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/msexceltables.c

This file parses Microsoft Excel BIFF workbook streams and dumps worksheet tables as text.

Key behavior:
- Reads BIFF records, dispatching on selected opcodes.
- Handles numbers, RK/MULRK values, labels, shared strings, booleans, errors, column widths, XF formats, date mode, BOF/EOF, and author/codepage metadata.
- Stores cells in sorted row/column linked lists per sheet.
- Outputs delimited, optionally quoted table rows with padding/truncation based on column widths.
- Supports worksheet/column range filters and dumping non-worksheet sheet types.

Important details:
- Supports BIFF8 Unicode strings and continuation records.
- Converts some built-in Excel number formats to date/time/percent/scientific text.
- Excel date conversion intentionally follows Excel's historical 1900 leap-year compatibility behavior.
- Default delimiter is a space; options control debug, all sheets, quoting, padding, truncation, delimiter, columns, and worksheets.

Filesystem relevance:
- Indirect: document stream parser intended for files exposed from compound documents, not filesystem implementation code.
