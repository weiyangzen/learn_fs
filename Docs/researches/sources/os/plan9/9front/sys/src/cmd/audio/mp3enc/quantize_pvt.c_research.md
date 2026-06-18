# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.c

This file provides shared private quantization data and helper routines: scalefactor-band tables, ATH computation, allowed-distortion computation, noise measurement, plotting data, and nonlinear quantizer lookup initialization.

Key responsibilities:
- Defines MPEG scalefactor partition tables:
  - `slen1_tab`, `slen2_tab`
  - `nr_of_sfb_block`
  - `pretab`
  - `sfBandIndex`
- Initializes quantization lookup tables:
  - `pow43`
  - `adj43`
  - `adj43asm`
  - `pow20`
  - `ipow20`
- Computes ATH per scalefactor band through `ATHmdct()` and `compute_ath()`.
- Converts L/R MDCT coefficients to M/S with `ms_convert()`.
- Allocates CBR target bits from perceptual entropy and reservoir availability via `on_pe()`.
- Reduces side-channel bit allocation in M/S stereo via `reduce_side()`.
- Converts psychoacoustic ratios into allowed quantization noise with `calc_xmin()`.
- Computes actual quantization noise and aggregate metrics with `calc_noise()`.
- Updates optional analysis/plotting structures through `set_pinfo()` and `set_frame_pinfo()`.
- Implements `quantize_xrpow()` and `quantize_xrpow_ISO()` for nonlinear quantization of `|xr|^(3/4)`.

Important functions:
- `iteration_init(lame_global_flags *gfp)`: one-time setup for ATH arrays, quantizer tables, and Huffman table chooser.
- `ATHmdct(...)`: converts ATH formula output into MDCT energy-domain threshold.
- `compute_ath(...)`: finds minimum ATH per long/short scalefactor band.
- `ms_convert(...)`: coefficient-domain M/S transform.
- `on_pe(...)`: target-bit allocation based on perceptual entropy.
- `reduce_side(...)`: shifts bits from side to mid channel based on side/mid energy ratio.
- `calc_xmin(...)`: computes `l3_xmin` masking thresholds per scalefactor band.
- `penalties(...)`: nonlinear noise penalty used in Klemm noise metric.
- `calc_noise(...)`: compares quantized reconstruction against original MDCT coefficients.
- `set_frame_pinfo(...)`: fills analysis fields after quantization.
- `quantize_xrpow(...)`: default quantizer using adjustment tables.
- `quantize_xrpow_ISO(...)`: ISO-style quantizer.

Control/data flow:
- `iteration_init()` is called before quantization begins and calls `huffman_init()` from `takehiro.c`.
- `quantize.c` calls `calc_xmin()` before `outer_loop()` and `calc_noise()` during noise shaping.
- `takehiro.c` calls `quantize_xrpow()` or `quantize_xrpow_ISO()` through `count_bits()`.
- Analysis mode uses `set_frame_pinfo()` after final signs and scalefactors are known.

Notable behavior:
- ATH scaling differs for nspsytune (`NSATHSCALE`) versus older model.
- `noATH` forces ATH thresholds down to near zero.
- `calc_xmin()` applies nspsytune bass/alto/treble shaping and optional temporal masking.
- For high-quality CBR/ABR nspsytune paths, `calc_xmin()` can aggressively lower thresholds by multiplying by `0.001`.
- There is optional `TAKEHIRO_IEEE754_HACK` code for faster float-to-int quantization; the default path uses portable casts and adjustment tables.

Dependencies:
- Includes `util.h`, `lame-analysis.h`, `tables.h`, `reservoir.h`, and `quantize_pvt.h`.
- Uses `ATHformula()` and internal ATH/scalefactor-band state from `lame_internal_flags`.

Risks and edge cases:
- Lookup arrays require quantized values to stay below `PRECALC_SIZE`; `count_bits()` checks against `IXMAX_VAL` before quantization.
- `compute_ath()` is declared in the header with `ATH_s[SBPSY_l]`, while short-block ATH arrays conceptually use `SBPSY_s`; the C ABI is unaffected but the declaration is misleading.
- `calc_noise()` assumes positive `l3_xmin` thresholds; extremely small thresholds can produce huge noise ratios.
- Optional IEEE754 hack is architecture-sensitive and disabled unless explicitly compiled.
