# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.c

PostScript inclusion engine for embedded picture pages. It scans a PostScript file for DSC sections, bounding boxes, globals, the requested page, and trailer, then emits wrapper PostScript from `ps_include.h` plus copied sections transformed/clipped/scaled into a target frame.

Key behavior:
- `copy` copies byte ranges line-by-line and prefixes `%` lines with a space so included DSC comments do not affect the outer document.
- `ps_include` scans for `%%Page`, `%%EndPage`, `%%PageBoundingBox`, `%%BoundingBox`, `%%EndProlog`, setup end comments, `%%Trailer`, and global blocks.
- Emits variables for bounding box, whiteout/outline/scale flags, center, size, adjustment, and rotation.
- Resets `curpostfontid`/`curfontsize` afterward to force state reestablishment.

Integration points:
- Used by `pictures.c`.
- Includes PostScript wrapper arrays from `ps_include.h`.

Risks:
- `global` pointer is only initialized through `grab` when globals are found; safe in normal flow but tightly coupled to `nglobal`.
- Page-bounding-box handling tests `i == page_no`, where `i` is last page number parsed, so ordering assumptions matter.
