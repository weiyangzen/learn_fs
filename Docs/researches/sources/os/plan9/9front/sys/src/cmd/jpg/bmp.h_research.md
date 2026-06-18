# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.h

This header defines BMP constants and header structures.

Key contents:
- Compression constants: RGB, RLE8, RLE4, and bitfields.
- `Rgb` palette entry struct.
- `Filehdr` and `Infohdr` structures matching BMP file and info header fields.
- `Filehdrsz` constant for the 14-byte file header.

Research notes:
- The structures use Plan 9 C scalar types and are likely read through helper code that handles little-endian layout.
