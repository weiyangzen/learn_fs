# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/output.c

Formats object coordinates and custom angle conversions.

Key points:
- `output` prints object or SAO star label, right ascension, declination, azimuth, elevation, semidiameter, and Sun/Moon magnitude/phase field.
- `Rconv` formats radians as hours/minutes/seconds.
- `Dconv` formats radians as signed degrees/minutes/seconds.

Dependencies:
- Installed by `main.c` as `%R` and `%D` formatters.

Notable behavior:
- Declination formatter folds values above 180 degrees into negative equivalents.
