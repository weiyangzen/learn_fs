# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps

Shell wrapper for distilling PostScript to PostScript through Ghostscript’s older `pswrite` device.

Behavior:

- Defaults to `-dSAFER`.
- Appends leading switches.
- Requires `input.ps output.ps`.
- Runs `gs -q -sDEVICE=pswrite -sOutputFile=... -dNOPAUSE -dBATCH`.

This is command glue for PostScript normalization.
