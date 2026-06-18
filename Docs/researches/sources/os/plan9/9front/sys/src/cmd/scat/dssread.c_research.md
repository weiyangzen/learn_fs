# File Research: sources/os/plan9/9front/sys/src/cmd/scat/dssread.c

Purpose: Reads and decompresses a DSS image tile into an `Img`.

Format handling:
- Expects a 21-byte header starting with `0xdd 0x99`.
- Reads big-endian `nx`, `ny`, `scale`, and total-sum fields.
- Last three header bytes carry quadrant bit-plane counts.

Key routines:
- `dssread`: opens a tile, validates header, allocates `Img`, decodes data, applies scale, runs inverse H-transform, and returns pixels.
- `dodecode`: initializes bit input, decodes four q-tree quadrants, checks EOF nybble, then reads sign bits.
- `getlong`: big-endian 32-bit helper.

Integration: Calls `qtree_decode`, `input_nybble`, `start_inputing_bits`, and `hinv`.

Risks:
- Allocation size is `sizeof(Img) + (nx*ny-1)*sizeof(int)`; malformed dimensions could overflow.
- Fatal exits on unexpected compressed-data errors.
