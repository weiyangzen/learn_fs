# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/printafm

Tiny shell wrapper for printing metrics from an AFM font.

It directly executes:

- `gs -q -dNODISPLAY -- printafm.ps "$@"`

Unlike nearby wrappers, it hardcodes `gs` rather than using `GS_EXECUTABLE`.
