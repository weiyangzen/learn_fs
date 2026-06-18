# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_11.h

Static psychoacoustic tuning tables for 11 kHz Vorbis encoding modes.

Important contents:
- `_psy_lowpass_11[3]` defines lowpass targets.
- `_psy_tone_masteratt_11[3]` defines tone master attenuation.
- `_vp_tonemask_adj_11[3]` defines tone-mask adjustment blocks.
- `_psy_noisebias_11[3]` defines low/mid/high noise bias curves across frequency bands.
- `_noise_thresh_11[3]` defines noise thresholds.

Integration points:
- Included by encoder mode setup code for low-sample-rate configurations.
- Uses types such as `att3`, `vp_adjblock`, and `noise3` from the mode/psychoacoustic setup headers.

Risk and review signals:
- Table-only file; changes affect encoder quality and bitrate allocation.
- Several high-frequency entries use `99` sentinel-style values because 11 kHz mode cannot use full 16 kHz-band tuning.

Filesystem relevance:
- No filesystem logic.
