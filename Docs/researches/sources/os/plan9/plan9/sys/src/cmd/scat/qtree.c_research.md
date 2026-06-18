# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/qtree.c

Decodes quadtree-compressed DSS bitplanes.

Key functions:
- `qtree_decode` decodes each bitplane either as direct packed bits or Huffman-expanded quadtree data.
- `qtree_expand` expands one quadtree level.
- `qtree_copy` expands 4-bit block values into 2x2 layout.
- `qtree_bitins` inserts decoded bit values into the output pixel array.
- `read_bdirect` reads direct packed 4-pixel nibbles for a bitplane.

Behavior notes:
- Scratch storage is sized from half-dimensions of the quadtree plane.
- Format code `0` means direct, `0xf` means Huffman quadtree; any other code is fatal.
- Uses the bit input helpers from `bitinput.c`.
