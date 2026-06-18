# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcfont.c

This file implements composite-font character operators, mainly `cshow` and `rootfont`.

Key behavior:
- `cshow` accepts the procedure and string in either order for Adobe compatibility.
- Sets up a C-show text enumerator and calls the user procedure for each character with character code and current width.
- During `cshow`, constructs an appropriately scaled leaf font when processing composite fonts and temporarily changes current font while preserving root/current font state.
- Restores root and current font after the user procedure using e-stack continuations.
- `rootfont` returns the current root font dictionary.

Important dependencies:
- Uses Ghostscript text enumerators from `gxtext.h`.
- Uses interpreter show setup/continuation helpers declared through `ichar.h`.
- Uses font and graphics state APIs from `ifont.h` and `igstate.h`.

Registered operators:
- `cshow`
- `rootfont`
- Internal `%cshow_continue`
- Internal `%cshow_restore_font`
