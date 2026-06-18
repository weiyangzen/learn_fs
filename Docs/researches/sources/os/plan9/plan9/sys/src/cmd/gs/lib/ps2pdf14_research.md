# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf14

Compatibility wrapper for PostScript-to-PDF 1.4.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.4 "$@"`

This selects Acrobat 5-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
