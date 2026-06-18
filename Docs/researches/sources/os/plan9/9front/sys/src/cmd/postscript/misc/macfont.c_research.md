# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/macfont.c

`macfont.c` converts Macintosh downloadable PostScript font files to Unix-style host-resident font files. It reads block sizes and types, skips comment blocks, writes ASCII text blocks with CR-to-LF conversion, converts binary data blocks to hex, stops on type 5, and errors on unimplemented resource types.

It mirrors `ibmfont.c`’s option and error style, but uses big-endian block-size parsing.
