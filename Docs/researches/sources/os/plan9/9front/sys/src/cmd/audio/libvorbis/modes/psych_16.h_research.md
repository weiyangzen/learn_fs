# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_16.h

Static psychoacoustic tuning tables for 16 kHz Vorbis encoding modes.

Important contents:
- `_psy_stereo_modes_16[4]` defines stereo coupling behavior by base quality.
- `_psy_lowpass_16[4]` defines lowpass targets.
- `_psy_tone_masteratt_16[4]` and `_vp_tonemask_adj_16[4]` define tone masking controls.
- `_psy_noisebias_16_short[4]`, `_psy_noisebias_16_impulse[4]`, and `_psy_noisebias_16[4]` define block-type-specific noise bias curves.
- `_psy_noiseguards_16[4]` defines noise guard parameters.
- `_noise_thresh_16[4]`, `_noise_start_16`, `_noise_part_16`, `_psy_ath_floater_16`, and `_psy_ath_abs_16` define noise normalization and ATH controls.

Integration points:
- Used by encoder setup paths targeting 16 kHz and nearby low-rate audio.

Risk and review signals:
- Static tuning only; no executable logic.
- Arrays have different lengths by purpose, so setup code must index with the correct mode family.
- `9999`/`99` values act as disabled/out-of-range sentinels.

Filesystem relevance:
- No filesystem logic.
