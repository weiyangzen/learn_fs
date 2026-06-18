# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.h

## Role
Public interface for Ghostgum's DSC parser used by Ghostscript/GSview-style consumers. It defines the parser object layout, DSC comment return codes, document/page metadata structures, error reporting enums, and the callable parser API.

## Contents
- Establishes local scalar types (`GSBOOL`, `GSDWORD`, `GSWORD`) and configurable `DSC_OFFSET`/format macros for file offsets.
- Defines parser sizing constants: legal DSC line length, string allocation chunk size, page allocation chunk size, and scan buffer length.
- Enumerates `CDSC_RETURN_CODE` values for recognized DSC comments across header, preview, defaults, prolog, setup, page, trailer, and EOF sections.
- Defines document metadata enums for preview type, page order, orientation, and binary/clean document data.
- Provides data structures for integer and floating bounding boxes, media descriptions, viewing orientation CTM, pages, DOS EPS headers, MacBinary headers, pooled string chunks, DCS 2.0 plate records, and process/custom colors.
- Defines DSC message identifiers, severity, and response codes.
- Declares `struct CDSC_s`, including public parsed document state plus private scanner state, callbacks, memory allocator hooks, string pool state, skip counters, and reference count.
- Declares the public lifecycle, scanning, callback, reference-counting, lookup, and display/debug APIs.

## Important Interfaces
- `dsc_init`, `dsc_init_with_alloc`, `dsc_free`, `dsc_new`, `dsc_ref`, `dsc_unref`.
- `dsc_set_length`, `dsc_scan_data`, `dsc_fixup`.
- `dsc_set_error_function`, `dsc_set_debug_function`, `dsc_debug_print`.
- `dsc_find_platefile`, `dsc_stricmp`, `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, `dsc_display`.

## Dependencies And Coupling
- Expects `size_t` to be visible from prior includes; this header itself does not include `<stddef.h>`.
- Exposes the full `CDSC` structure rather than an opaque handle, so clients can inspect and possibly depend on layout details.
- References `dsc_known_media` and `dsc_message` tables implemented elsewhere.
- The artificial `char dummy[1024]` at the start of `struct CDSC_s` is unusual and affects ABI/layout compatibility.

## Risks And Notes
- Default `DSC_OFFSET` is `unsigned long`, which may be 32-bit on some targets and insufficient for large PostScript/PDF inputs.
- Uses C strings and manual allocation callbacks; callers must respect parser ownership of stored string/media/page pointers.
- API exposes internal helper functions for GSview PDF handling, so implementation changes may have external compatibility impact.

## Filesystem Relevance
Indirect only. It parses file-stream metadata and tracks byte offsets into documents, but it does not implement filesystem behavior.
