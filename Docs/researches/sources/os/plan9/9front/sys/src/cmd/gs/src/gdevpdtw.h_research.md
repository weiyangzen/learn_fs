# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.h

Private font and CMap resource-writing API for pdfwrite.

Key behavior:
- Declares font content writers matching `pdf_font_write_contents_proc_t`: Type 0, Type 3 finish, standard, simple, CIDFontType0, and CIDFontType2.
- Declares encoding helper APIs for finding differing encoding indexes and writing encoding objects/references.
- Forward-declares `gs_cid_system_info_t` and `gs_cmap_t`.
- Declares CIDSystemInfo and CMap writing functions.

Research notes:
- The comments state these procedures are intended to be called only from `gdevpdtf.c`.
- The header is the public edge of `gdevpdtw.c`; most implementation detail stays private.
