# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdfopt

Shell wrapper for optimizing a PDF through Ghostscript’s `pdfopt.ps`.

Behavior:

- Defaults options to `-dSAFER -dDELAYSAFER`.
- Appends leading command-line switches.
- Requires `input.pdf output.pdf`.
- Executes Ghostscript quietly in no-display mode with `pdfopt.ps`.

This is a utility wrapper, not a library module.
