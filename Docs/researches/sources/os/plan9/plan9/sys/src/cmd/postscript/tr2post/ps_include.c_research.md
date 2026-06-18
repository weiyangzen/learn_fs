# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.c

Purpose: Includes selected pages from an existing PostScript file into the current PostScript output.

Key behavior:
- Scans DSC comments for prologue/setup boundaries, page boundaries, page/global definitions, trailer, and bounding boxes.
- Defaults bounding box to US Letter dimensions if none is found.
- Emits a PostScript wrapper that saves/restores state, disables page operators, clips/scales/rotates/translates the included page, and optionally whiteouts/outlines.
- Copies prologue, global definitions, selected page, and trailer.
- `copy` indents lines beginning with `%` to neutralize nested DSC comments without breaking encodings.
- Resets current font cache after inclusion.

Dependencies and integration:
- Called from `pictures.c`.
- Uses wrapper fragments declared in `ps_include.h`.

Risks and notes:
- `%%PageBoundingBox` handling relies on the current `i` page number from previous parsing, which is fragile.
- DSC parsing is simple and may not handle all valid PostScript documents.
- `global` allocation uses dynamic grow-by-20 sections.
