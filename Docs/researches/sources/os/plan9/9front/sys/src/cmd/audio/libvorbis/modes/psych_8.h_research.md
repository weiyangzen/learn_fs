# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_8.h

Static psychoacoustic tuning tables for 8 kHz Vorbis encoding.

Important contents:
- `_psy_tone_masteratt_8[3]` and `_vp_tonemask_adj_8[3]` define tone masking controls.
- `_psy_noisebias_8[3]` defines noise bias curves.
- `_psy_stereo_modes_8[3]` defines low-sample-rate stereo coupling behavior.
- `_psy_noiseguards_8[2]` defines noise guard parameters.
- `_psy_compand_8[2]` defines companding tables.
- `_psy_lowpass_8[3]`, `_noise_start_8`, `_noise_part_8`, `_psy_ath_floater_8`, and `_psy_ath_abs_8` define lowpass, noise normalization, and ATH controls.

Integration points:
- Used by encoder mode setup for 8 kHz audio.

Risk and review signals:
- Static table-only file.
- High frequency bands use `99` sentinels because 8 kHz audio has limited bandwidth.
- Array lengths differ by category, so setup code must use correct indexes.

Filesystem relevance:
- No filesystem logic.
