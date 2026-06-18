# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/takehiro.c

This file implements MP3 Huffman table selection, quantized coefficient bit counting, scalefactor-storage optimization, and Huffman-region refinement.

Key responsibilities:
- Chooses optimal Huffman tables for quantized coefficient regions.
- Counts bits for big-values and count1 regions.
- Sets `big_values`, `count1`, `table_select[]`, `region0_count`, `region1_count`, and `count1table_select` in `gr_info`.
- Recalculates better region divisions after quantization.
- Applies `scfsi` sharing between MPEG-1 granules where legal.
- Optimizes scalefactor storage (`scalefac_scale`, `preflag`, `scalefac_compress`, `part2_length`).
- Initializes per-bigvalue scalefactor-region lookup tables in `huffman_init()`.

Important functions:
- `ix_max(...)`: maximum quantized coefficient in a region.
- `count_bit_ESC(...)`: bit count for escape-code Huffman tables.
- `count_bit_noESC(...)`, `count_bit_noESC_from2(...)`, `count_bit_noESC_from3(...)`: fast bit counts for non-escape table families.
- `choose_table_nonMMX(...)`: selects best Huffman table for a coefficient pair region.
- `count_bits_long(...)`: counts bits for a complete granule/channel and fills Huffman side-info fields.
- `count_bits(...)`: quantizes `xrpow`, checks `IXMAX_VAL`, and calls `count_bits_long()`.
- `best_huffman_divide(...)`: tries alternative region divisions and count1 boundaries.
- `scfsi_calc(...)`: marks reusable long-block scalefactor bands in MPEG-1 second granule.
- `best_scalefac_store(...)`: removes scalefactors from zero bands, optionally halves scalefactors via `scalefac_scale`, applies `scfsi`, and updates part2 length.
- `scale_bitcount(...)`: MPEG-1 scalefactor bit count and compress selection.
- `scale_bitcount_lsf(...)`: MPEG-2/2.5 LSF scalefactor bit count and compress selection.
- `huffman_init(...)`: selects MMX/non-MMX table chooser and precomputes `bv_scf`.

Control/data flow:
- `quantize.c` calls `count_bits()` repeatedly during global-gain and outer noise-shaping loops.
- After final quantization, `quantize.c` calls `best_scalefac_store()` and optionally `best_huffman_divide()`.
- `iteration_init()` in `quantize_pvt.c` calls `huffman_init()` once during quantization setup.

Notable behavior:
- The table chooser has hard-coded knowledge of MPEG Huffman table families.
- Quantized coefficients beyond `IXMAX_VAL` cause `count_bits()` to return `LARGE_BITS`.
- Short-block MPEG-2 Huffman division optimization is explicitly skipped.
- `best_scalefac_store()` can set second-granule scalefactors to `-1` to indicate `scfsi` reuse.
- `scale_bitcount_lsf()` reverse-engineers MPEG-2 scalefactor compression partitioning and sets `slen[]`.

Dependencies:
- Includes `util.h`, `l3side.h`, `tables.h`, and `quantize_pvt.h`.
- Uses lookup tables from `tables.c` and quantizer kernels from `quantize_pvt.c`.

Risks and edge cases:
- This file is bitstream-critical; incorrect region counts or table choices produce invalid MP3 frames.
- Several optimizations depend on MPEG version, block type, and scalefactor-band boundaries.
- The MMX path is conditional and requires an external `choose_table_MMX()` symbol if enabled.
- Some assertions around region counts are commented out, so unusual boundary cases rely on later clamping.
