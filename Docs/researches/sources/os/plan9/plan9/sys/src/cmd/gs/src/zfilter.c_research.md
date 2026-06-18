# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfilter.c

## Purpose
Creates common PostScript stream filters and provides generic filter-open machinery for string, file, and procedure sources/targets.

## Key Functions
- `zAXE()`, `zAXD()`, `zNullE()`, `zPFBD()`, `zPSSE()`, `zRLE()`, `zRLD()`, `zSFD()`, and `zEOFD()` create filters.
- `filter_read()` and `filter_write()` create filter file objects over source/target strings, files, or procedures.
- `filter_ensure_buf()` inserts or allocates intermediate buffering when needed.
- `filter_mark_temp()` and `filter_mark_strm_temp()` mark temporary filter streams for close cleanup.

## Important Behavior
- Optional filter dictionaries can supply `CloseSource` or `CloseTarget`.
- Procedure operands are converted through `sread_proc()` / `swrite_proc()`.
- String sources/targets are wrapped as temporary streams.
- `SubFileDecode` supports the LL3 dictionary form with `EODCount`/`EODString`.

## Research Notes
Shared interpreter-side filter framework used by the specialized filter files in this group.
