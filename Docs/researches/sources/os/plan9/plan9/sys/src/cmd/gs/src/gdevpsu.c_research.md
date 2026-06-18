# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.c

This file provides shared utilities for Ghostscript PostScript-writing devices, especially DSC file/page headers and trailers.

Low-level support:
- `psw_print_lines` writes a null-terminated array of strings to a `FILE *`.
- `psw_put_procset_name` and `psw_print_procset_name` generate a ProcSet name from device name, language level, and ProcSet version.
- `psw_print_bbox` writes DSC `BoundingBox` and `HiResBoundingBox` comments.
- `is_seekable` uses `fstat(fileno(f))` and `S_ISREG` to determine whether an output `FILE *` can be rewound to patch a placeholder bounding box.

File-level API:
- `psw_begin_file_header` writes `%!PS-Adobe-3.0` or EPS headers, bounding-box comments or placeholders, creator/date/document/language comments, prolog boilerplate, copyright text, ProcSet resource setup, and page-size-setting procedures.
- `psw_end_file_header` closes the prolog/resource setup.
- `psw_end_file` writes the trailer and page count, patches or appends bounding boxes when needed, and writes `%%EOF` for non-EPS output.

Page-level API:
- `psw_write_page_header` writes DSC page setup, begins the ProcSet, sets page size for non-EPS output, creates page save/dictionary state, optionally scales from device pixels to PostScript points, and starts page content with `gsave mark`.
- `psw_write_page_trailer` clears/restores page state, handles copy count, and emits `showpage` or `copypage`.

The only direct filesystem-like behavior is seeking within regular output files to fill fixed-width bounding-box placeholder lines. Otherwise, this is a presentation-format helper.
