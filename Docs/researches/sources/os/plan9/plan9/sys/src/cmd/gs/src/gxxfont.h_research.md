# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxxfont.h

Defines Ghostscript’s external font, or xfont, interface. The design comments establish that devices supply xfonts, xfonts are transformation-specific bitmap providers, and allocation/release is mediated through object procedures.

Core API:
- `gx_xfont_common` and `gx_xfont_s`: generic xfont object with a procedure table.
- `gx_xfont_procs_s`: factory lookup, glyph mapping, metrics, render, and release methods.
- `xfont_proc_*` macros: stable prototypes for implementation tables.
- `gs_private_st_dev_ptrs1`: GC descriptor helper for xfonts that reference one device pointer.

The file is part of rendering/device integration. The main portability concern is ABI stability of callback signatures and GC relocation for device-backed font objects.
