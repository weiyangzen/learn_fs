# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.c

Vorbis psychoacoustic analysis implementation, excluding pre-echo envelope handling.

Important routines:
- `_vp_global_look()` and `_vp_global_free()` allocate/free global psychoacoustic lookups.
- `_vi_gpsy_free()` and `_vi_psy_free()` free setup structures.
- `setup_tone_curves()` builds tone masking curves from ATH and tonemask tables.
- `_vp_psy_init()` initializes per-block psychoacoustic lookups: ATH, Bark windows, octave maps, tone curves, and noise offsets.
- `_vp_psy_clear()` releases lookup allocations.
- `_vp_noisemask()` computes hybrid Bark-domain noise masks with companding.
- `_vp_tonemask()` computes tone masks using seed curves and ATH floor.
- `_vp_offset_and_mix()` combines tone/noise masks and applies AoTuV MDCT compensation.
- `_vp_ampmax_decay()` decays amplitude max over time.
- `_vp_couple_quantize_normalize()` performs noise normalization, quantization, and stereo/multichannel coupling.

Important data:
- `stereo_threshholds` and `stereo_threshholds_limited` drive coupling thresholds.
- `FLOOR1_fromdB_LOOKUP` converts floor dB indexes to linear scale.
- Internal helpers implement seed curve propagation, Bark noise regression, lossless flags, and noise normalization.

Integration points:
- Declared by `psy.h`.
- Used by encoder mapping/floor/residue paths.
- Depends on `masking.h`, `smallft.h`, `scales.h`, `codec_internal.h`, and setup tables.

Risk and review signals:
- Allocation-heavy hot paths use `malloc()` without explicit failure checks.
- Coupling/normalization code is numerically sensitive and affects bitstream quality.
- Several comments document AoTuV tuning behavior; changes need audio regression coverage.
- Static lookup duplicates floor1 dB conversion logic for encode-side coupling.

Filesystem relevance:
- No filesystem logic. This is audio psychoacoustic encode logic.
