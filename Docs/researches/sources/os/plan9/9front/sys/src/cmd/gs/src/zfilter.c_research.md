# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter.c

## Purpose
Creates common PostScript stream filters and provides the generic filter-open machinery for string, file, and procedure sources/targets.

## Key Functions
- `zAXE()`, `zAXD()`, `zNullE()`, `zPFBD()`, `zPSSE()`, `zRLE()`, `zRLD()`, `zSFD()`, and `zEOFD()` create specific filters.
- `rl_setup()` reads RunLength `EndOfData`.
- `filter_read()` and `filter_write()` create filter file objects over source/target strings, files, or procedures.
- `filter_read_simple()` and `filter_write_simple()` wrap the common no-parameter cases.
- `s_Null1D_process()` implements byte-at-a-time NullDecode for buffering.
- `s_EOFD_process()` implements immediate EOF for unknown PDF filter handling.
- `filter_ensure_buf()` inserts or allocates intermediate buffering when a downstream stream buffer is too small.
- `filter_mark_temp()` and `filter_mark_strm_temp()` mark temporary filter streams for close cleanup.

## Important Behavior
- Optional filter dictionaries can supply `CloseSource` or `CloseTarget`.
- Procedure operands are converted through `sread_proc()` / `swrite_proc()`.
- String sources/targets are wrapped as temporary streams.
- Filter buffer sizes are raised to template minimums and default to at least `file_default_buffer_size` for small minimums.
- `SubFileDecode` supports the LL3 dictionary form with `EODCount`/`EODString`.

## Research Notes
This is the shared interpreter-side filter framework used by the specialized filter files in this group.
