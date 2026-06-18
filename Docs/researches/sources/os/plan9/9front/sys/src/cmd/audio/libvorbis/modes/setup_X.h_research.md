# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_X.h

Catch-all quality-only setup templates used when bitrate mapping should be disabled.

Important contents:
- Defines `rate_mapping_X`, a 12-entry array of `-1` values.
- Defines `ve_setup_X_stereo` and `ve_setup_X_uncoupled` using 44 kHz-style setup data and no bitrate hints.
- Defines `ve_setup_XX_stereo` and `ve_setup_XX_uncoupled` using 8 kHz-style setup data and no bitrate hints.

Integration points:
- Reuses 44 kHz symbols for `ve_setup_X_*`.
- Reuses 8 kHz symbols for `ve_setup_XX_*`.
- Intended for quality modes only, as documented in the file header.

Risk and review signals:
- Static setup data only.
- Header inclusion order matters for all referenced 44 kHz and 8 kHz symbols.
- `rate_mapping_X` uses 12 entries even for the 8 kHz setup, which only consumes the first quality-count entries.
- `ve_setup_X_uncoupled` passes `NULL` for stereo modes, while `ve_setup_XX_uncoupled` uses `_psy_stereo_modes_8`.

Filesystem relevance:
- No filesystem logic. It is encoder setup fallback data.
