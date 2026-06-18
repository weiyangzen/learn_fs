# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/wftopfa

Tiny shell wrapper around Ghostscript’s `wftopfa.ps`.

It sets `GS_EXECUTABLE=gs` and runs:

- `gs -q -dNODISPLAY -- wftopfa.ps "$@"`

Purpose: execute the associated PostScript font-conversion helper.
