# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/toppm.c

Command-line Netpbm converter. It reads a Plan 9 image, converts to a multi-channel memory image where needed, and writes PBM/PGM/PPM through `memwriteppm`.

Options support a single-line comment and raw output mode (`P4/P5/P6`) versus text output (`P1/P2/P3`). For file input it synthesizes a default conversion comment if none is provided.

It rejects comments containing newlines to preserve valid Netpbm comment formatting.
