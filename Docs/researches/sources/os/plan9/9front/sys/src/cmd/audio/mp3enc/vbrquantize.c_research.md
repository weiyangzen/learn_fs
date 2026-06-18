# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vbrquantize.c

LAME variable-bitrate quantization path for MPEG Layer III frames.

Key responsibilities:
- Computes scalefactor-band quantization noise with optional IEEE754 conversion shortcuts.
- Searches scalefactor values that keep quantization error below psychoacoustic masking thresholds.
- Computes MPEG-1 and LSF long/short block scalefactors, including `scalefac_scale`, `preflag`, and short-block subblock gain.
- Builds scaled `xr34` arrays for long and short blocks using selected scalefactors.
- Quantizes granules, counts Huffman bits, optionally applies best-Huffman division, and returns encoding status.
- Implements two VBR noise-shaping strategies: the older iterative path and `VBR_noise_shaping2()` with fallback to CBR-like binary step-size search.
- Top-level `VBR_quantize()` calculates masking thresholds, silence detection, min/max bit budgets, reservoir constraints, quality adjustment, final bitrate index selection, scalefactor storage optimization, and sign restoration.

Dependencies:
- Uses `util.h`, `l3side.h`, `quantize.h`, `reservoir.h`, `quantize_pvt.h`, and analyzer structures.
- Relies on tables/macros such as `pow43`, `adj43`, `pretab`, `POW20`, `IPOW20`, `IXMAX_VAL`, `LARGE_BITS`, and MPEG scalefactor-band constants.

Research notes:
- This file is algorithmically dense and stateful; most operations mutate `gfc->l3_side` granule/channel metadata.
- The top-level VBR loop lowers quality and bit limits until total frame bits fit the reservoir-permitted frame budget.
- Several branches preserve historical LAME tuning experiments and compile-time optimization paths.
