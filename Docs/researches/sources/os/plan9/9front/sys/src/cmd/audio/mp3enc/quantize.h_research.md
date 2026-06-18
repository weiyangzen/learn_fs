# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.h

This header declares the public quantization entry points used by the frame encoder and VBR modules.

Exports:
- `iteration_loop(...)`: CBR frame quantization.
- `VBR_iteration_loop(...)`: VBR quantization/bitrate selection.
- `ABR_iteration_loop(...)`: ABR quantization/bitrate selection.
- `VBR_quantize(...)`: alternate VBR quantizer implemented elsewhere.
- `VBR_noise_shaping2(...)`: per-granule VBR noise-shaping helper used by `vbr_mtrh`.

Dependencies:
- Includes `util.h`, which provides `lame_global_flags`, `FLOAT8`, `III_psy_ratio`, `III_scalefac_t`, and related encoder types.

Integration:
- Included by `encoder.c` and quantization-related modules.
- The declarations route all frame-level MDCT/psychoacoustic output into quantized `l3_enc` coefficients and scalefactors.

Risks and edge cases:
- The header exposes large fixed-size array contracts such as `[2][2][576]`; callers must preserve granule/channel/coefficient layout exactly.
- `VBR_quantize()` and `VBR_noise_shaping2()` are declared here but not implemented in `quantize.c`, so link completeness depends on the companion VBR source.
