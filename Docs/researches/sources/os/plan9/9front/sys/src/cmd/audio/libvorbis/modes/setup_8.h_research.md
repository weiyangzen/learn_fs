# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_8.h

Top-level encoder setup template for 8 kHz Vorbis modes.

Important contents:
- Includes `psych_8.h` and `residue_8.h`.
- Defines fixed block size `{512,512}`.
- Defines one floor mapping selecting floor index 6.
- Defines stereo bitrate mapping `{6000,9000,32000}` and uncoupled mapping `{8000,14000,42000}`.
- Defines quality mapping `{-0.1,0.0,1.0}`.
- Defines `_psy_compand_8_mapping` and `_global_mapping_8`.
- Defines `ve_setup_8_stereo` and `ve_setup_8_uncoupled`.

Integration points:
- Uses 8 kHz psychoacoustic, noise, lowpass, ATH, stereo mode, floor, and residue templates.
- Provides base tables reused by `setup_11.h` and `setup_X.h`.

Risk and review signals:
- Static setup data only.
- Only three quality points and fixed block sizes, so tuning changes are broad.
- Stereo and uncoupled modes differ mainly in rate mapping, coupling field, and residue mapping template.

Filesystem relevance:
- No filesystem logic. It is low-rate audio encoder configuration.
