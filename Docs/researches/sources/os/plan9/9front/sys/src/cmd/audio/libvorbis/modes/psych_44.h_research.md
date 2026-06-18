# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_44.h

Large static psychoacoustic tuning header for 44.1/48 kHz Vorbis encoding.

Important contents:
- `_psy_global_44[5]` defines global preecho trigger settings, postecho thresholds, stretch penalty, and minimum energy for quality tiers.
- `_psy_compand_44[6]` defines noise compander lookup blocks for short/long and low/mid/high quality modes.
- `_vp_tonemask_adj_longblock[12]` and `_vp_tonemask_adj_otherblock[12]` define tonal masking adjustment curves.
- `_psy_noisebias_trans[12]`, `_psy_noisebias_long[12]`, `_psy_noisebias_impulse[12]`, and `_psy_noisebias_padding[12]` define noise bias curves by block type and quality.
- `_psy_noiseguards_44[4]`, `_psy_tone_suppress[12]`, `_psy_tone_0dB[12]`, and `_psy_noise_suppress[12]` define guard/suppression behavior.
- `_psy_info_template` provides a default `vorbis_info_psy` structure.
- `_psy_ath_floater[12]` and `_psy_ath_abs[12]` define ATH tuning.
- `_psy_stereo_modes_44[12]` maps quality tiers to stereo coupling points.
- `_psy_tone_masteratt_44[12]`, `_psy_lowpass_44[12]`, noise start/partition arrays, and noise thresholds define high-level quality-dependent tuning.

Integration points:
- Consumed by encoder mode setup code for full-band 44.1/48 kHz presets.
- Values influence `mapping0_forward()` indirectly through psychoacoustic lookups and global settings.

Risk and review signals:
- Static tuning dominates encoder quality; changes require audio regression tests, not just compile tests.
- Contains historical commented-out alternative tunings and sentinel values such as `99` and `9999`.
- There are visually suspicious initializer fragments like `-7  -3` without a comma in some adjustment blocks; this is valid C tokenization as arithmetic subtraction but should be treated carefully if editing.

Filesystem relevance:
- No filesystem logic.
