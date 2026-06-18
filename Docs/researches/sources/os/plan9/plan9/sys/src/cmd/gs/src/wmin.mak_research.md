# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wmin.mak

Makefile fragment for compiling Wadalab free Kanji font chunks into the executable.

Key points:
- Defines `ccfonts_ps=gs_kanji gs_ccfnt`.
- Groups many generated `wmin*.obj` files into `ccfonts1_` through `ccfonts7_`.
- Corresponding source/base names are listed in `ccfonts1` through `ccfonts7`.
- Comments state it does not include rules for creating the `wmin*.c` files.

Dependencies and interactions:
- Used by compiled-font support.
- Relates to Ghostscript initialization/font resources rather than platform code.

Research relevance:
- Historical compiled-in Japanese font resource list.
