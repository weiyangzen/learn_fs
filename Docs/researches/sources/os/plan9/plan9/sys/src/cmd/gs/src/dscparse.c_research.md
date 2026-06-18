# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.c

## Purpose

`dscparse.c` implements a streaming parser for Adobe Document Structuring Convention comments, based mainly on DSC 3.0 with selected DSC 2.1 and DCS extensions. It extracts document/page metadata, section offsets, media, bounding boxes, page order, orientation, preview information, color separations, and error/fixup state.

## Public API

- `dsc_init`, `dsc_init_with_alloc`, `dsc_new`, `dsc_ref`, `dsc_unref`, and `dsc_free` manage parser lifetime.
- `dsc_set_length` optionally constrains parsing to a known document length.
- `dsc_scan_data` accepts incremental buffers and advances the parser state.
- `dsc_fixup` finalizes partial or malformed DSC and reconciles section/page metadata.
- `dsc_set_error_function` and `dsc_set_debug_function` install caller callbacks.
- `dsc_add_page`, `dsc_add_media`, and `dsc_set_page_bbox` let callers augment parsed data, including PDF-derived metadata.
- `dsc_find_platefile` maps DCS separation pages to external EPS filenames.
- `dsc_stricmp` provides local case-insensitive comparison.

## Parser Architecture

- The parser is state-machine based, with sections for type detection, comments, preview, defaults, prolog, setup, pages, trailer, and EOF.
- Input is buffered in `CDSC_DATA_LENGTH` chunks, with offsets tracked so section/page byte ranges can be reported.
- `dsc_scan_type` detects PostScript/DSC, EPSF, PJL wrappers, Control-D prefix, DOS EPS headers, PDF headers, MacBinary EPSF, and AppleSingle/AppleDouble wrappers.
- `dsc_read_line` handles CR, LF, CRLF, DOS Ctrl-Z, embedded `%%BeginData`, `%%BeginBinary`, and nested `%%BeginDocument` skipping.
- Metadata parsing functions handle pages, bounding boxes, floating bounding boxes, orientation, page order, media, viewing orientation, and page labels.
- `dsc_scan_*` functions parse allowed comments per DSC section and propagate lines when a section boundary is encountered.

## Metadata Handled

- Document identity: title, creator, creation date, `%%For`, language level, document data mode.
- Page structure: `%%Pages`, `%%Page`, page labels, ordinals, begin/end byte offsets, page order.
- Geometry: `%%BoundingBox`, `%%HiResBoundingBox`, `%%CropBox`, page bounding boxes, page crop boxes, viewing orientation.
- Media: `%%DocumentMedia`, `%%PageMedia`, and older DSC 2.1 paper size/color/form/weight comments.
- Preview/container formats: EPSI, DOS EPS TIFF/WMF, Mac PICT previews.
- Color/separations: `%%DocumentProcessColors`, `%%DocumentCustomColors`, `%%CMYKCustomColor`, `%%RGBCustomColor`, DCS 1.0 plate comments, and DCS 2.0 `%%PlateFile`.

## Error Handling / Fixups

- Error severities are table-driven via `dsc_severity`.
- If no error callback is installed, errors default to “assume DSC was correct” behavior.
- `dsc_fixup` handles common malformed inputs: early trailers/EOF, page-count mismatches, missing EPS bounding boxes, EPS files with multiple pages, missing default media, unlabeled pages, and DCS 2.0 page exposure.
- Begin/end counters validate font, feature, resource, and procset blocks.

## Memory Model

- Supports caller-supplied allocators.
- Uses chunked string storage (`CDSCSTRING`) for persistent parsed strings.
- Dynamically grows page and media arrays.
- Frees per-page boxes/orientation, media boxes, DCS lists, color lists, Mac/DOS wrapper metadata, and string chunks during reset/free.

## Filesystem Relevance

This is document-structure parsing, not filesystem code. It is relevant to file-oriented workflows because it records byte offsets for document sections/pages and can identify external DCS plate filenames, but it does not open, read, or write files directly.

## Research Notes

- The parser is deliberately tolerant of real-world malformed PostScript/EPS files.
- Streaming behavior is central: callers can feed partial buffers, and the parser requests more data when container headers or lines are incomplete.
- `%%+` continuation support is intentionally limited to comments where repeated parameter sets are expected.
