# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/bdftops

Tiny shell wrapper around Ghostscript’s `bdftops.ps`.

It sets `GS_EXECUTABLE=gs` and then executes:

- `gs -q -dBATCH -dNODISPLAY -- bdftops.ps "$@"`

Purpose: run the PostScript helper that converts BDF font data to PostScript form. The executable name is intended to be patched during installation.
