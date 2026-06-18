# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/macfont.c

Macintosh downloadable PostScript font converter.

Key responsibilities:
- Converts Macintosh font resource blocks to Unix-readable font files.
- Reads big-endian block length, block type, and a following unused byte.
- Skips comment blocks.
- Emits ASCII blocks with CR converted to newline.
- Emits binary blocks as uppercase hex, wrapping every 40 bytes.
- Stops on type 5.

Options:
- `-D` enables debug output.
- `-I` ignores fatal errors.

Notable risks:
- Types 3 and 4 are explicitly unimplemented fatal cases.
- Uses old K&R style and sparse EOF validation.
