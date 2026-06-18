# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inftrees.c

Source read: complete file, 304 lines.

Purpose: Builds canonical Huffman decoding tables for inflate. `inflate_table()` converts symbol bit lengths into compact `code` tables used by the inflate state machine and fast decoder.

Key interface:
- `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` returns `0` on success, `-1` for invalid over-subscribed or incomplete code sets, and `1` when the caller-provided `ENOUGH_*` capacity is insufficient.

Implementation notes:
- Counts code lengths, finds min/max lengths, adjusts requested root bits, handles the no-symbol case by emitting invalid markers, and validates prefix-code completeness.
- Sorts symbols by length into the caller-provided `work[]` array.
- Chooses base and extra-bit tables for literal/length and distance codes, including end-of-block handling for symbol 256.
- Fills root and sub-tables by replicating entries over unused high index bits and creates sub-table pointers when code lengths exceed root width.
- Updates `*table` to the next free entry and `*bits` to the actual root table width.

Integration:
- Called by `hammer2_zlib_inflate.c` for code-length, literal/length, and distance trees.
- Uses `ENOUGH_LENS` and `ENOUGH_DISTS` from `hammer2_zlib_inftrees.h` to guard table growth.

Risks and review notes:
- The function assumes all `lens[]` entries are in `0..MAXBITS`; callers must validate or construct lengths safely.
- If root table sizes in inflate are changed, `ENOUGH_LENS` and `ENOUGH_DISTS` must be recalculated or this function can return capacity failure.
