# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/laserbar.c

`laserbar.c` emits PostScript for Code 39 barcodes. It maps supported characters to wide/narrow bar patterns, supports rotation, offsets, x/y scaling, optional labels, optional `newpath`, and optional `showpage`.

The core `laserbar()` writes PostScript helper definitions and encodes a start/stop `*` plus each input character. Lowercase letters are accepted and labeled uppercase.
