# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf13

Compatibility wrapper for PostScript-to-PDF 1.3.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.3 "$@"`

This selects Acrobat 4-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
