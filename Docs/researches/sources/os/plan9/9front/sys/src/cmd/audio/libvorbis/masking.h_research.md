# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/masking.h

Static psychoacoustic masking data for Vorbis tone and absolute-threshold calculations.

Important contents:
- Defines `MAX_ATH` and `ATH[]`, a detailed absolute threshold of hearing table.
- Defines `EHMER_OFFSET`, `EHMER_MAX`, and a large `tonemasks[P_BANDS][6][EHMER_MAX]` table.
- Tone mask data covers frequency bands from low bass through 16 kHz, with masking curves for multiple tone levels and offsets.
- Uses `-999` sentinel-style values for inactive/out-of-range curve regions.

Integration points:
- Included by psychoacoustic code, not directly by the files in this group.
- Depends on `P_BANDS` and related psychoacoustic types/macros from `psy.h`.

Risk and review signals:
- This is calibration data; changes affect encoder quality and bitrate behavior, not parser safety.
- Table dimensions must remain consistent with psychoacoustic code expectations.
- No executable logic is present.

Filesystem relevance:
- No filesystem logic. It is static audio psychoacoustic tuning data.
