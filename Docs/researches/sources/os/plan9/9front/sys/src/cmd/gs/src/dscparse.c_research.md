# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.c

This is Russell Lang/Ghostgum's DSC parser implementation for Ghostscript and GSview integration. It parses Adobe Document Structuring Conventions comments in streaming PostScript/EPS input, records document/page metadata and byte offsets, handles several wrapper formats, and repairs common DSC errors after scanning.

Key responsibilities:
- Provides public parser lifecycle and API functions:
  - `dsc_init`, `dsc_init_with_alloc`, `dsc_new`, `dsc_ref`, `dsc_unref`, and `dsc_free`.
  - `dsc_set_length` to bound parsing when the caller knows file length.
  - `dsc_scan_data` to stream chunks of input through the parser.
  - `dsc_fixup` to finalize partial state, repair offsets, and validate consistency.
  - `dsc_set_error_function` and `dsc_set_debug_function`.
  - `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, and `dsc_find_platefile`.
- Detects document type and wrappers: `%!PS-Adobe`, EPSF, generic PostScript, PDF marker, PJL prefix, DOS EPS binary header, MacBinary EPSF, AppleSingle/AppleDouble, and leading Ctrl-D.
- Tracks DSC sections and byte offsets for comments, preview, defaults, prolog, setup, pages, trailer, and EOF.
- Parses high-value DSC comments: page count/order/orientation, bounding boxes, hires bounding boxes, crop boxes, document media, page media, page labels/ordinals, viewing orientation, document data type, DCS plate files, process colors, and custom colors.
- Skips embedded data safely through `%%BeginData`, `%%BeginBinary`, and recursive `%%BeginDocument`/`%%EndDocument` tracking.
- Supports several DSC 2.1 paper/media comments discontinued in DSC 3.0, including paper sizes, forms, colors, weights, and `%%PaperSize:`.
- Converts DCS 2.0 single-file and multi-file plate information into page-like records for separation extraction.

Parsing architecture:
- `dsc_scan_data` appends caller data into an internal fixed buffer, moves consumed data forward, identifies type on first input, then repeatedly reads complete lines and dispatches them to section-specific scanners.
- `dsc_read_line` handles CR, LF, CRLF, partial lines, Ctrl-Z, long-line warnings, skipped binary bytes, skipped lines, and embedded-document boundaries.
- Section scanners are state-machine functions:
  - `dsc_scan_comments`
  - `dsc_scan_preview`
  - `dsc_scan_defaults`
  - `dsc_scan_prolog`
  - `dsc_scan_setup`
  - `dsc_scan_page`
  - `dsc_scan_trailer`
- `CDSC_PROPAGATE` lets a line that begins a new section be reprocessed by the next section scanner.
- `CDSC_NEEDMORE` is used when a wrapper/header or partial line needs more bytes.
- `CDSC_NOTDSC` tells callers to ignore DSC metadata for the document.

Important data handling:
- Strings are stored in chunked arenas via `dsc_alloc_string`; parsed line snippets are normalized by `dsc_add_line`.
- Pages grow in chunks of `CDSC_PAGE_CHUNK`.
- Media records are deep-copied into parser-owned allocations.
- Known built-in media include Letter, Legal, Ledger, A3/A4/A5, B4/B5, Note, and 11x17.
- `dsc_copy_string` handles DSC/PostScript-style parenthesized strings and escape sequences.
- Numeric helpers parse integers/reals from bounded line fragments.
- Endian helpers decode DOS EPS little-endian and Mac formats big-endian headers.

Error and fixup behavior:
- Error severity defaults are stored in `dsc_severity`; actual user policy is delegated to the optional `dsc_error_fn`.
- Without an error callback, `dsc_error` silently returns `CDSC_RESPONSE_CANCEL`, effectively assuming DSC comments are correct.
- `dsc_fixup` flushes final data, repairs unfinished embedded sections, joins adjacent sections, handles code between setup and first page, extends a last page to the final trailer, validates page counts, checks EPS bounding-box/page rules, assigns default media, and fills missing page labels.
- The parser detects and reports duplicate header/trailer comments, early trailer/EOF, page ordinal errors, incorrect `atend` usage, unmatched Begin/End blocks, long lines, and bad section placement.

DCS/color support:
- `dsc_parse_platefile` parses DCS 2.0 `%%PlateFile:` lines for single-file offset/length separations or multi-file local EPS separations.
- `dsc_parse_dcs1plate` maps `%%CyanPlate:`, `%%MagentaPlate:`, `%%YellowPlate:`, and `%%BlackPlate:` into DCS-like records.
- `dsc_dcs2_fixup` exposes DCS separations as pages and adjusts composite-page boundaries.
- `dsc_parse_process_colours`, `dsc_parse_custom_colours`, `dsc_parse_cmyk_custom_colour`, and `dsc_parse_rgb_custom_colour` maintain linked `CDSCCOLOUR` metadata.

Important relationships:
- Built by `int.mak` as part of `dscparse.dev` with `zdscpars.c`; `usedsc.dev` includes it with PostScript support code.
- `zdscpars.c` uses this C parser as one part of Ghostscript's higher-level DSC parsing interface.
- The parser is independent of direct file I/O: it consumes caller-provided buffers and stores offsets relative to the stream.

Notable implementation details and risks:
- It is robust against many historical malformed DSC/EPS cases, but also preserves permissive behavior through caller decisions or default silent handling.
- It uses fixed-size local buffers (`MAXSTR`, `DSC_LINE_LENGTH`, `CDSC_DATA_LENGTH`) and truncation/long-line handling rather than unbounded allocations.
- `dsc_scan_type` treats PDF only as a marker and does not parse PDF content; public helpers let GSview add PDF-derived pages/media externally.
- The code contains old C idioms and manual memory management, with correctness depending on the `CDSC` structure contract in `dscparse.h`.
- The parser is byte-offset oriented, so callers can later extract page ranges, previews, or DCS plate sections from the original document stream.

Filesystem relevance:
- There is no filesystem implementation or storage-layer behavior.
- The file is relevant to file-format parsing in Ghostscript: it interprets PostScript/EPS document structure and records byte ranges, but all I/O is external to the parser.

Research classification: streaming DSC/EPS metadata parser and repair layer used by Ghostscript's PostScript interpreter integration.
