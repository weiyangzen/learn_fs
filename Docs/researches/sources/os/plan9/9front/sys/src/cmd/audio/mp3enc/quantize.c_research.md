# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.c

This file implements the main Layer III quantization loops for CBR, VBR, and ABR encoding. It takes MDCT coefficients plus psychoacoustic masking ratios and produces quantized spectral coefficients, scalefactors, Huffman-side information, bitrate selection, and reservoir updates.

Key responsibilities:
- Initializes per-granule/channel quantization state with `init_outer_loop()`.
- Searches global gain and quantizer step sizes via `bin_search_StepSize()` and `inner_loop()`.
- Runs the outer noise-shaping/scalefactor amplification loop with `outer_loop()`.
- Chooses better quantization candidates through configurable `quant_compare()` policies.
- Adjusts scalefactor scale, subblock gain, and per-band amplification through helper loops.
- Implements final post-quantization steps in `iteration_finish()`: scalefactor storage optimization, optional Huffman-region optimization, reservoir accounting, and coefficient sign restoration.
- Provides three public frame quantizers:
  - `iteration_loop()` for CBR.
  - `VBR_iteration_loop()` for VBR.
  - `ABR_iteration_loop()` for average bitrate mode.

Important internal functions:
- `init_outer_loop(...)`: resets `gr_info`, clears scalefactors, computes `xrpow = |xr|^(3/4)`, and detects digital silence.
- `bin_search_StepSize(...)`: finds an initial global gain that approaches a bit target.
- `inner_loop(...)`: raises global gain until Huffman bits fit a max bit budget.
- `loop_break(...)`: detects whether every scalefactor band has already been amplified.
- `quant_compare(...)`: compares noise metrics under `experimentalX` modes.
- `amp_scalefac_bands(...)`: amplifies bands whose noise exceeds the trigger.
- `inc_scalefac_scale(...)`: converts scalefactors to doubled step size where possible.
- `inc_subblock_gain(...)`: tries to reduce oversized short-block scalefactors by raising subblock gain.
- `balance_noise(...)`: coordinates scalefactor amplification and bitcount validity checks.
- `outer_loop(...)`: main noise-shaping iteration.
- `VBR_encode_granule(...)`: binary-searches a good per-granule bit count for acceptable VBR noise.
- `get_framebits(...)`, `calc_min_bits(...)`, `calc_max_bits(...)`, `VBR_prepare(...)`: VBR bit budget setup.
- `calc_target_bits(...)`: ABR target bit calculation.

Public functions:
- `iteration_loop(...)`
- `VBR_iteration_loop(...)`
- `ABR_iteration_loop(...)`
- `bin_search_StepSize(...)`
- `inner_loop(...)`

Control/data flow:
- The encoder passes `xr`, `ratio`, `pe`, and M/S energy ratios into one of the public loops.
- Each granule/channel initializes `cod_info`, `scalefac`, and `xrpow`.
- `calc_xmin()` from `quantize_pvt.c` converts psychoacoustic thresholds into allowed distortion.
- `outer_loop()` repeatedly quantizes, counts bits, measures distortion, and amplifies scalefactor bands until quality or loop-stop criteria are met.
- `count_bits()` and Huffman helpers in `takehiro.c` calculate coding length and table selections.
- `best_scalefac_store()` and `best_huffman_divide()` refine side-info storage after final quantization.
- Reservoir functions assign and reconcile available bits.

VBR behavior:
- `VBR_prepare()` optionally converts LR to MS coefficients, computes quality-dependent masking lower factors, detects analog silence, and computes min/max bit budgets.
- `VBR_iteration_loop()` first estimates needed bits, chooses the smallest bitrate that can hold them, and may retry with relaxed thresholds or repartitioned budgets.
- `vbr_mtrh` delegates per-granule quantization to `VBR_noise_shaping2()` from `vbrquantize.c`.

ABR behavior:
- `calc_target_bits()` starts from target average bitrate, adds bits based on perceptual entropy, caps by max frame capacity, and reduces side-channel allocation in MS mode.
- `ABR_iteration_loop()` then selects the lowest allowed bitrate index capable of holding the final frame.

CBR behavior:
- `iteration_loop()` asks reservoir code for target/extra bits, allocates based on PE, optionally converts LR to MS, and quantizes each granule/channel within the current frame budget.

Dependencies:
- Includes `util.h`, `l3side.h`, `quantize.h`, `reservoir.h`, `quantize_pvt.h`, and `lame-analysis.h`.
- Uses MPEG bitrate tables from `tables.c` through headers.
- Depends heavily on `lame_internal_flags` state: bitrate index, mode granules, side info, noise-shaping flags, VBR bounds, scalefactor bands, and reservoir size.

Risks and edge cases:
- Quantization loops depend on many mutable globals in `gfc`; retry paths must restore `cod_info`, `scalefac`, and `xrpow` carefully.
- `inc_subblock_gain()` computes `width = scalefac_band.s[sfb] - scalefac_band.s[sfb+1]`, which is negative for normal ascending scalefactor bands; that makes its later loop inert and looks like a latent bug or old-code typo.
- `bin_search_StepSize()` mutates `gfc->CurrentStep` using a heuristic that depends on prior frames.
- Several bit budgets are bounded by hard constants such as `MAX_BITS`, `LARGE_BITS`, and magic PE thresholds.
- VBR loops can retry while relaxing thresholds if used bits exceed frame capacity; correctness depends on convergence and valid bitrate bounds.
