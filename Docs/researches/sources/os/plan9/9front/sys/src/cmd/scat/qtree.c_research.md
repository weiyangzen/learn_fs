# File Research: sources/os/plan9/9front/sys/src/cmd/scat/qtree.c

Purpose: Decodes DSS q-tree compressed bit planes into pixel coefficient arrays.

Key routines:
- `qtree_decode`: loops through bit planes, handling direct bitmap or q-tree/Huffman-coded formats.
- `qtree_expand`: expands one quadtree level and reads new Huffman values for nonzero nodes.
- `qtree_copy`: expands 4-bit node values into 2x2 child bits.
- `qtree_bitins`: inserts decoded bit-plane bits into `Pix` output.
- `read_bdirect`: handles directly encoded nybble-packed bitmaps.

Integration: Called by `dssread.c`; uses `input_nybble` and `input_huffman` from `bitinput.c`.

Risks:
- Assumes output image array was zero-initialized.
- Exits on bad format code or memory failure.
- Has special handling for odd image dimensions.
