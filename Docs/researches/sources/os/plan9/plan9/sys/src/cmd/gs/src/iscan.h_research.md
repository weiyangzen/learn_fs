# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.h

Purpose: defines scanner state, dynamic accumulation buffers, binary scanning substate, scanner options, special return codes, and public scanner entry points.

Key structures:
- `dynamic_area` tracks base/next/limit pointers, dynamic-vs-buffer ownership, the local comment-sized buffer, and allocator.
- `scan_binary_state` stores number format, continuation function, object array, current index, string/object bounds, top-level size, and sequence byte size.
- `scanner_state` stores procedure-building stack depths, options, current scan mode, dynamic area, and unioned substate for binary, names, and string filters.

Options include string-source scanning, syntax-check-only mode, comment/DSC processing, PDF scan rules, and Adobe-compatible invalid-number behavior. Return codes distinguish ordinary tokens from binary object sequences, EOF, refills, comments, and DSC comments.

The header exposes `st_scanner_state` so saved scanner states can be allocated and traced by the Ghostscript GC.
