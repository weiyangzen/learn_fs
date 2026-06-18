# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.c

PostScript page-order reverser for DSC-structured documents. It copies the prologue/setup, records page byte offsets, moves `%%BeginGlobal`/`%%EndGlobal` sections into the prologue/setup, writes pages in reverse physical-sheet order, handles multiple forms per page, and copies the trailer.

Key behavior:
- Accepts one file or copies stdin to a temporary file.
- Recognizes `%%EndProlog`, optional setup comments, `%%Page:`, `%%EndPage:`, `%%Trailer`, and package-specific `%%BeginGlobal` comments.
- `-r` disables reversal but still extracts globals; `-n` controls forms-per-page; `-o` selects output pages; `-v` ignores old forms prologue compatibility.
- Uses fixed `Pages pages[1000]` for page ranges and dummy pages needed by forms-per-page reversal.

Integration points:
- Uses shared DSC constants and helpers from `comments.h`, `gen.h`, `path.h`, `ext.h`.
- Uses `tempnam`/`temp_file` from the shared support layer.

Risks:
- Hard page cap of 1000 can overflow for larger documents; no bounds check before `pages[next_page++]`.
- Stdin path reads the input three times via a temporary file.
- Correctness depends on page independence except for recognized global blocks.
