# File Research: sources/os/plan9/9front/sys/src/cmd/aux/msexceltables.c

`msexceltables` reads BIFF Excel workbook streams and prints sheet contents as delimited text. It handles BIFF8 Unicode strings, shared string tables, worksheet records, numeric cells, inline labels, booleans/errors, RK compressed numbers, multiple RK records, column widths, date modes, and XF format indices.

The file builds an in-memory sorted row/column linked structure per sheet, then dumps it with padding, truncation, optional rc-style quoting, sheet and column range filters, and a configurable delimiter. Date/time formatting is recognized for selected built-in Excel format IDs, with Lotus 1-2-3/Excel 1900 leap-year compatibility noted in epoch comments.

The BIFF parser reads records with `getrec`, dispatches selected opcodes, and skips unhandled record payloads. `gstr` handles BIFF8 continuation records, Unicode/byte modes, rich-text runs, and Asian phonetic extension bytes.

Options: `-D` debug hex dump, `-a` all sheet types, `-q` no quoting, `-d` delimiter, `-n` no padding, `-t` truncate, `-c` column range, `-w` worksheet range.

Caveats: only a subset of BIFF records and formats is implemented; range parser uses 1-based position in output iteration; several malformed files cause `sysfatal`.
