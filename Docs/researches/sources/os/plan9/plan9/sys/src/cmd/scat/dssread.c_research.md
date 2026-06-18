# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/dssread.c

Reads and decodes compressed DSS image tile files.

Key functions:
- `dssread` validates the DSS magic header, reads dimensions/scale/sum metadata, allocates `Img`, decodes pixels, rescales if needed, applies inverse H-transform, and returns the image.
- `dodecode` decodes three quadtree-compressed bitplane groups into image quadrants, validates padding nybble, and applies sign bits.
- `getlong` reads big-endian 32-bit header fields.

Behavior notes:
- The image payload is reconstructed with `qtree_decode`, `input_nybble`, and `hinv`.
- `ip->a[0]` is initialized from the header sum before inverse transform.
- Bad format or EOF exits fatally with `"format"`.
