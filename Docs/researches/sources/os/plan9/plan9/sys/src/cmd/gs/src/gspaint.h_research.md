# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.h

Declares the public painting API for Ghostscript graphics state users.

Exports:
- `gs_erasepage`
- `gs_fillpage`
- `gs_fill`
- `gs_eofill`
- `gs_stroke`
- `gs_imagepath`

Integration:
- Requires `gsstate.h` types to be visible before inclusion.
- Implemented mainly in `gspaint.c`; `gs_imagepath` is declared here but implemented elsewhere.

Risk notes:
- This is a thin API header with no ownership logic; correctness depends on caller-supplied valid `gs_state *`.
