# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/ibmfont.c

IBM PC downloadable PostScript font converter.

Key responsibilities:
- Converts IBM PC segmented font files to Unix-readable font files.
- Parses segments with leading byte 128, type, and 4-byte little-endian length.
- Emits ASCII segments with CR converted to newline.
- Emits binary segments as uppercase hex, wrapping every 40 bytes.
- Stops on EOF segment type 3.

Options:
- `-D` enables debug segment prints.
- `-I` ignores fatal errors.

Notable risks:
- Old K&R C style with minimal validation.
- Reads bytes with `getc()` without checking EOF inside fixed-size segment loops.
