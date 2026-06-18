# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.h

This private header exposes quantization internals shared by `quantize.c`, `quantize_pvt.c`, `takehiro.c`, and related encoder modules.

Key definitions:
- `IXMAX_VAL`: maximum allowed quantized coefficient plus linbits margin.
- `PRECALC_SIZE`: quantizer lookup table size.
- `Q_MAX`: size for `pow20`/`ipow20` global gain tables.
- `LARGE_BITS`: sentinel bit count for impossible encodings.
- `calc_noise_result`: aggregate quantization-noise metrics.

Exported data:
- MPEG scalefactor tables: `nr_of_sfb_block`, `pretab`, `slen1_tab`, `slen2_tab`, `sfBandIndex`.
- Quantizer tables: `pow43`, `adj43`, `adj43asm`, `pow20`, `ipow20`.

Exported functions:
- ATH and M/S helpers: `compute_ath()`, `ms_convert()`.
- Bit allocation: `on_pe()`, `reduce_side()`.
- Quantization search: `bin_search_StepSize()`, `inner_loop()`, `iteration_init()`.
- Noise and thresholds: `calc_xmin()`, `calc_noise()`, `set_frame_pinfo()`.
- Quantizer kernels: `quantize_xrpow()`, `quantize_xrpow_ISO()`.
- Huffman/scalefactor helpers from `takehiro.c`: `count_bits()`, `best_huffman_divide()`, `best_scalefac_store()`, `scale_bitcount()`, `scale_bitcount_lsf()`, `huffman_init()`.

Dependencies:
- Includes `l3side.h` for side-info, scalefactor, and psychoacoustic types.

Risks and edge cases:
- This header deliberately exposes mutable global lookup arrays; initialization order via `iteration_init()` matters.
- Several functions accept large fixed-size arrays by pointer; dimension mismatches will not be caught by C.
- The `compute_ath()` short-array bound is misleading (`SBPSY_l`) even though the implementation iterates short bands separately.
