# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/pictures.c

Picture inclusion support for `tr2post`. It parses `x X PI`/`PictureInclusion` arguments, opens the referenced PostScript picture, computes frame size/position/rotation/alignment flags, restores the current page save state, calls `ps_include`, then restores page state.

Integration points:
- Called from `devcntl.c`.
- Calls `ps_include` from `ps_include.c`.
- Uses `devres`, `hpos`, `vpos`, and global `picflag`.
- Contains disabled `#ifdef UNDEF` code for inline picture packing/copying.

Risks:
- Inline picture support is documented but disabled.
- `picopen` calls `error(FATAL)` on open failure despite caller also checking for `NULL`, so warning recovery path is mostly unreachable.
- Fixed-size `name`, `hwo`, and `flags` buffers can truncate long picture arguments.
