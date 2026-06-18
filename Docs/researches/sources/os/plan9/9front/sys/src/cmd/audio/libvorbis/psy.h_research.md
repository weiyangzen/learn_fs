# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.h

Header for Vorbis psychoacoustic setup and lookup structures.

Important contents:
- Defines psychoacoustic constants: `EHMER_MAX`, `P_BANDS`, `P_LEVELS`, `P_NOISECURVES`, and `NOISE_COMPAND_LEVELS`.
- Defines `vorbis_info_psy`, containing block flag, ATH tuning, tone mask settings, noise mask settings, companding, max curve dB, and normalization controls.
- Defines `vorbis_info_psy_global`, containing octave resolution, envelope thresholds, amplitude decay, coupling controls, and sliding lowpass settings.
- Defines `vorbis_look_psy_global` and `vorbis_look_psy` runtime lookup structures.
- Declares psychoacoustic lifecycle, masking, amplitude decay, and coupling/quantization routines.

Integration points:
- Included by `codec_internal.h`, `psy.c`, and encoder paths.
- Depends on `smallft.h`, `backends.h`, and `envelope.h`.
- Couples setup-table data to runtime encoder analysis.

Risk and review signals:
- Raw pointer ownership is manual; callers must pair init/clear functions.
- Constants fix array dimensions used by many static setup tables.
- Struct layout is private to this vendored libvorbis tree but broad within the codec.

Filesystem relevance:
- No filesystem logic. It is audio encoder analysis API/state.
