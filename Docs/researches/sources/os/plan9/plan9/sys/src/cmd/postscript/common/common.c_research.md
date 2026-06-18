# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.c

Plan 9-specific shared PostScript translator helpers.

Key responsibilities:
- Defines PostScript string escaping table `charcode`.
- Tracks page, line, character, and output-string state.
- Parses selected page lists.
- Emits page start/end PostScript scaffolding.
- Copies files to `Bstdout`.
- Provides allocation and diagnostic helpers.

Important behavior:
- `pagelist()` stores selected pages in a bitmap.
- `pageon()` suppresses output and temporarily disables debug for unselected pages.
- `startstring()`/`endstring()` coalesce text into PostScript strings at current `hpos/vpos`.
- `startpage()` and `endpage()` emit DSC page comments, save/restore, setup, showpage, and end-page comments.

Dependencies:
- Uses Plan 9 `Biobuf`, `Bstdout`, `Bstderr`, and globals declared in `common.h`.

Notable risks:
- Page bitmap grows by page number and never shrinks.
- `pagelist()` has permissive parsing and no validation of malformed ranges.
