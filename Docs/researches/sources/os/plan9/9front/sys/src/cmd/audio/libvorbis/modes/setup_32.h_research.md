# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_32.h

Top-level encoder setup template for 32 kHz modes, reusing 44 kHz psychoacoustic/residue infrastructure with 32 kHz rate mappings.

Important contents:
- Defines 12-point stereo and uncoupled bitrate mappings.
- Defines `_psy_lowpass_32` with lower lowpass values at lower quality and `99` for high quality.
- Defines `ve_setup_32_stereo` and `ve_setup_32_uncoupled`.

Integration points:
- Relies on 44 kHz symbols such as `quality_mapping_44`, `blocksize_short_44`, `blocksize_long_44`, `_psy_tone_masteratt_44`, `_floor_mapping_44`, and `_mapres_template_44_*`.
- Stereo uses `_psy_stereo_modes_44`; uncoupled passes `NULL` for stereo modes.
- Uses the same floor books/floors as 44 kHz.

Risk and review signals:
- Header inclusion order matters because it assumes 44 kHz setup symbols are already available.
- Static setup data only.
- Uncoupled rate mapping is substantially higher than stereo mapping at low qualities.

Filesystem relevance:
- No filesystem logic. This is audio encoder setup configuration.
