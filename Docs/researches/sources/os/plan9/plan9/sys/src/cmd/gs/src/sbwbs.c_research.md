# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.c

Implementation of Burrows-Wheeler block-sorting compression filters.

The file first defines common buffered-block stream support:

- `s_buffered_set_defaults`, `s_buffered_no_block_init`, and `s_buffered_block_init`.
- `s_buffered_process`, which fills a block buffer from stream input.
- `s_buffered_release`.

For `BWBlockSortEncode`:

- Allocates a block buffer and rotation index array.
- Reverses the input block before encoding so the decoder emits the original order.
- Sorts rotations using an initial radix pass and `qsort` with `bwbs_compare_rotations`.
- Writes the block length `N` and primary index `I` as big-endian `int` values.
- Emits the Burrows-Wheeler transformed last-column bytes.

For `BWBlockSortDecode`:

- Reads `N` and `I`, validates them, fills the encoded block, and constructs inverse mapping tables.
- Uses `SHORT_OFFSETS` by default, storing inverse-order data in 64K, 4K, and 12-bit packed tiers to save memory.
- Iterates from index `I` through the inverse transform to reconstruct output bytes.

Risk notes: the encoder uses a static `bwbs_compare_ss` to pass state to `qsort`, so the sort comparison is not reentrant. Several allocation comments are marked “WRONG” in the legacy source.

This is compression transform code, not filesystem logic.
