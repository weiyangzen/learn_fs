# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_16.h

Top-level encoder setup template for 16 kHz Vorbis modes.

Important contents:
- Includes `psych_16.h` and `residue_16.h`.
- Defines short block sizes `{1024,512,512}` and long block sizes `{1024,1024,1024}`.
- Defines two floor mapping arrays: `_floor_mapping_16a` and `_floor_mapping_16b`.
- Defines stereo and uncoupled bitrate mappings with four points.
- Defines `_global_mapping_16`, `quality_mapping_16`, and `_psy_compand_16_mapping`.
- Defines `ve_setup_16_stereo` and `ve_setup_16_uncoupled`.

Integration points:
- Uses 16 kHz psychoacoustic tables for tone, noise, ATH, lowpass, and stereo modes.
- Uses `_mapres_template_16_stereo` and `_mapres_template_16_uncoupled`.
- Reuses `_psy_compand_8` with 16 kHz compand mappings.

Risk and review signals:
- Static setup only; data shape must match `ve_setup_data_template`.
- Quality mapping has four points, not the 12-point 44 kHz scheme.
- Floor mapping count is `2`; callers must not select a third mapping.

Filesystem relevance:
- No filesystem logic. This is audio encoder setup data.
