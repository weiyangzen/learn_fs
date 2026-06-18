# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclbits.c

Implements command-list bitmap, tile, and transfer-map writing support.

Key behavior:
- `clist_bitmap_bytes` computes written bitmap size and row width after selective raster-padding removal; compressed data keeps full raster, while small/one-line/spread bitmaps can drop padding.
- `cmd_put_bits` writes bitmap payloads into clist command buffers, optionally trying CCITTFax or RLE compression when worthwhile and legal for the reader buffer.
- Falls back to uncompressed short-row data when compression fails or is not beneficial; returns `limitcheck` if a bitmap cannot fit in the reading buffer and cannot be decompressed elsewhere.
- Emits tile-parameter commands with encoded depth, replication dimensions, optional repetition factors, and optional shift.
- Emits tile-index commands either as small deltas from the previous band state or as absolute indices.
- Emits color-map commands for none, identity, or explicit transfer-map values, using IDs to suppress redundant output.
- Maintains a clist tile/bitmap cache keyed by bitmap id using an open-addressed hash table and the generic bits-cache allocator.
- Deletes cache entries by freeing the bits-cache block, clearing the hash slot, and deleting later entries that would otherwise require relocation incompatible with band-list references.
- Adds tile slots with per-band known masks, cached bitmap metadata, and copied source bits.
- Chooses replicated tile parameters to improve playback efficiency while respecting cache size, max repetitions, shift constraints, and tile byte caps.
- `clist_change_tile` ensures tile parameters and bits are known in a band before tile-rectangle operations, writing parameter and bit commands when needed.
- `clist_change_bits` performs similar per-band caching for copy operations and can promote frequently seen character bitmaps to all bands when the configured threshold is reached.

Dependencies:
- Uses `gxcldev.h` command encodings and writer helpers, `gxdevmem.h`, compression stream states, bits-cache support, and transfer-map structures.

Research notes:
- The cache is coupled to band-list state: per-band masks track which bands know a cached tile, while hash slots may be deleted independently.
- Compression is opportunistic and bounded by `cbuf_size`; the code prioritizes playback buffer constraints over maximum compression ratio.
- `CHAR_ALL_BANDS_COUNT` is set to `max_ushort`, so this build never automatically broadcasts character bitmaps to all bands based on reuse count.
