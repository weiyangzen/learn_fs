# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/ibmfont.c

`ibmfont.c` converts IBM PC downloadable PostScript font resource files into Unix-style host-resident font files. It reads segment headers beginning with byte 128, dispatches ASCII text blocks with CR-to-LF conversion, converts binary blocks to uppercase hex with line wrapping, and stops on EOF segment type.

It includes simple `-D` debug and `-I` ignore-fatal options plus local legacy error handling.
