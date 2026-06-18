# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/font2c

Tiny shell wrapper around Ghostscript’s `font2c.ps`.

It sets `GS_EXECUTABLE=gs` and runs:

- `gs -q -dNODISPLAY -dWRITESYSTEMDICT -- font2c.ps "$@"`

Purpose: execute the PostScript helper that converts font data to C-source form.
