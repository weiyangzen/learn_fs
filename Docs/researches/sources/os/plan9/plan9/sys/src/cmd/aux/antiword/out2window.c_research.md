# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/out2window.c

## Summary
`out2window.c` converts buffered paragraph and table text into Antiword’s `diagram_type` output abstraction. It handles line movement, alignment, justification, outline numbering, and fixed-width table fallback rendering.

## Main Responsibilities
- Emits linked `output_type` substrings via `vSubstring2Diagram()`.
- Computes net line width after trimming trailing whitespace.
- Aligns text left, right, centered, or justified by adding spaces across whitespace “holes”.
- Maintains heading counters for outline-style numbering.
- Formats Word table rows into text-window lines when XML table output does not handle them.
- Computes column widths from Word twips, character width, and paragraph-break magnification.

## Key Dependencies
Uses output dispatch functions from `output.c`, text-width helpers, table row metadata, list numbering helpers from `misc.c`, and UTF-8/column-count utilities.

## Filesystem Relevance
No direct filesystem interaction. This is userland presentation logic for document output.

## Notes
The table fallback assumes fixed-width font behavior and skips rows whose parsed column count does not match row metadata.
