# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/p9bitpost.c

`p9bitpost.c` is a command-line Plan 9 image-to-PostScript converter. It parses dpi, debug, magnification, landscape, PostScript patch string, and paper size options; reads a `Memimage`; initializes `pslib`; applies options; and emits one-page PostScript with `image2psfile()`.

Defaults target US letter dimensions in points.
