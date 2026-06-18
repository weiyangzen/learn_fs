# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_22.h

Top-level encoder setup template for 22 kHz modes, built mostly from 16 kHz tables with 22 kHz rate/lowpass adjustments.

Important contents:
- Defines `rate_mapping_22` and `rate_mapping_22_uncoupled`.
- Defines `_psy_lowpass_22`.
- Defines `ve_setup_22_stereo` and `ve_setup_22_uncoupled`.

Integration points:
- Reuses 16 kHz block sizes, floor mappings, quality mapping, companding, noise guards, noise bias, ATH, stereo modes, and residue templates.
- Expects `setup_16.h`-provided symbols to be in scope before this header is used.
- Uses `_mapres_template_16_stereo` and `_mapres_template_16_uncoupled`.

Risk and review signals:
- Header dependency order matters; it does not include `setup_16.h` itself.
- Static tuning data only.
- Lowpass values `{9.5,11,30,99}` define the major 22 kHz-specific behavior.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder preset data.
