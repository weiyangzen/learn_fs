# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/topng.c

Command-line PNG converter. It reads a Plan 9 image as `Memimage`, accepts optional comment and gamma metadata, then writes PNG through `memwritepng`.

The `ImageInfo` flags indicate which optional PNG chunks to emit. The `-t` option is accepted but ignored in this file.

All image encoding details are delegated to `writepng.c`; this file mainly handles argument parsing, input opening, and output setup.
