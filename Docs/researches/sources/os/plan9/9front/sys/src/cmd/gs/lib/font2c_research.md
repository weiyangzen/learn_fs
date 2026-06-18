# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/font2c

Small shell wrapper invoking Ghostscript `font2c.ps`.

Behavior:
- Defines install-time-substituted `GS_EXECUTABLE=gs`.
- Runs Ghostscript with `-q -dNODISPLAY -dWRITESYSTEMDICT -- font2c.ps "$@"`.

Filesystem relevance:
- External process wrapper only.
