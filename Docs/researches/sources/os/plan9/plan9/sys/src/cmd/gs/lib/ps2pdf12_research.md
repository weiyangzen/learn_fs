# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf12

Compatibility wrapper for PostScript-to-PDF 1.2.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.2 "$@"`

This selects Acrobat 3-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
