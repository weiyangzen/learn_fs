# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsnd

Minimal no-display Ghostscript wrapper.

It sets `GS_EXECUTABLE=gs` and executes:

- `gs -dNODISPLAY "$@"`

Purpose: run Ghostscript as a non-display PostScript interpreter with caller-supplied arguments.
