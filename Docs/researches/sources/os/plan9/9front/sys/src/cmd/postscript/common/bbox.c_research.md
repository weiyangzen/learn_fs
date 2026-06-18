# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/bbox.c

`bbox.c` tracks PostScript page and document bounding boxes. `cover()` expands the current user-space box; `writebbox()` transforms it through the current transformation matrix, applies slop, emits DSC bounding-box comments, and updates the document box; `resetbbox()` starts a new page box.

It also implements basic CTM operations: `scale`, `translate`, `rotate`, and `concat`. The code is intended for translators that only count pages actually written to stdout.
