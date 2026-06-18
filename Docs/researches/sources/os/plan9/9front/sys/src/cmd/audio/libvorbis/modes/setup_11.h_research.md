# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_11.h

Top-level encoder setup template for 11 kHz Vorbis modes.

Important contents:
- Includes `psych_11.h`.
- Defines fixed block size `{512,512}` for both short and long paths.
- Defines floor mapping `_floor_mapping_11a` selecting floor index 6.
- Defines stereo bitrate mapping `{8000,13000,44000}` and uncoupled mapping `{12000,20000,50000}`.
- Defines quality mapping `{-0.1,0.0,1.0}`.
- Defines `ve_setup_11_stereo` and `ve_setup_11_uncoupled`.

Integration points:
- Reuses many 8 kHz tables: `_psy_noiseguards_8`, `_psy_compand_8`, `_noise_start_8`, `_noise_part_8`, `_global_mapping_8`, `_psy_stereo_modes_8`, and `_mapres_template_8_*`.
- Uses 11 kHz-specific tone, noise bias, lowpass, and threshold tables.

Risk and review signals:
- Static setup data only.
- Stereo uses coupling indicator `2`; uncoupled uses `-1`.
- Low-rate setup uses one floor mapping set and fixed block sizes, so changes have broad effect across all 11 kHz qualities.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder preset configuration.
