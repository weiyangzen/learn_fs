# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf

Compatibility wrapper for PostScript-to-PDF conversion.

Behavior:

- Documents that the default currently targets PDF 1.4 but may change.
- Executes `ps2pdf14 "$@"`.

The actual Ghostscript invocation is delegated through `ps2pdf14` to `ps2pdfwr`.
