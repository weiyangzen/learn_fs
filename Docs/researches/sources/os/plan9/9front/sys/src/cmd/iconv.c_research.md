# File Research: sources/os/plan9/9front/sys/src/cmd/iconv.c

Implements an image channel converter for Plan 9 image files.

Key points:
- Usage: `iconv [-u] [-c chanstr] [file]`.
- Reads a `Memimage` from stdin or one file.
- Parses target channel descriptor with `strtochan`; defaults to the source channel.
- Allocates a destination `Memimage` with the same rectangle and target channel.
- Uses `memimagedraw` to convert/copy pixels between channel formats.
- Writes either compressed image format via `writememimage` or uncompressed Plan 9 image format with `-u`.
- `writeuncompressed` writes the textual image header and each scanline from `unloadmemimage`.

Dependencies and interactions:
- Uses Plan 9 draw/memdraw libraries.

Research relevance:
- A small command-line wrapper around Plan 9 image channel conversion and image serialization.
