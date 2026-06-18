# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icfontab.c

Builds the compiled-font procedure table.

Key points:
- Includes `ccfont.h`.
- Uses `gconfigf.h` or `GCONFIGF_H` to declare compiled-font procedures via `font_` macros.
- Builds `fprocs[]`, a null-terminated array of compiled font initializer function pointers.
- `ccfont_fprocs` returns the number of procedures, the table pointer, and `ccfont_version`.

Research notes:
- This file is compiled and linked with compiled fonts, possibly in a shared library.
- Compatibility is checked by returning the font ABI version.
