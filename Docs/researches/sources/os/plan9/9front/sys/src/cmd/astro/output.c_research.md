# File Research: sources/os/plan9/9front/sys/src/cmd/astro/output.c

Formatting support for `astro` point output.

Important behavior:
- `output` prints object name/SAO id, right ascension, declination, azimuth, elevation, semi-diameter, and Sun/Moon phase magnitude.
- `Rconv` formats radians as hours/minutes/seconds.
- `Dconv` formats radians as signed degrees/minutes/seconds.

Registered by `main.c` with Plan 9 `fmtinstall`.
