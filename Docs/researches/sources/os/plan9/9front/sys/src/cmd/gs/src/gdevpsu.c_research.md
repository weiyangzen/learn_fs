# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.c

This file provides shared utilities for PostScript-writing devices.

Low-level support:
- `psw_print_lines` writes a null-terminated array of strings to a `FILE *`.
- `psw_put_procset_name` and `psw_print_procset_name` generate a ProcSet name from device name, language level, and ProcSet version.
- `psw_print_bbox` writes DSC `BoundingBox` and `HiResBoundingBox` comments.
- `is_seekable` uses `fstat(fileno(f))` and `S_ISREG` to decide whether a `FILE *` can be rewound to patch the bounding box.

File-level API:
- `psw_begin_file_header` writes `%!PS-Adobe-3.0` or EPS header, bounding box placeholder/atend/fixed bbox, creator/date/document data/language comments, prolog, copyright, ProcSet resource, and shared page-size-setting procedures.
- `psw_end_file_header` closes the prolog/resource setup.
- `psw_end_file` writes trailer and page count, patches or appends bounding box if necessary, and writes `%%EOF` for non-EPS output.

Page-level API:
- `psw_write_page_header` writes DSC page setup, begins the ProcSet, sets page size for non-EPS output, creates the page save/dict, optionally scales from device pixels to PostScript points, and starts page content with `gsave mark`.
- `psw_write_page_trailer` clears/restores page state, handles copy count, and emits `showpage` or `copypage`.

The file is an output-format helper. Its only direct filesystem-like behavior is checking whether the output file is seekable and patching fixed-width bounding-box placeholder lines later.
