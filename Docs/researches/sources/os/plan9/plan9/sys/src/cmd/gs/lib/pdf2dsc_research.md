# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2dsc

Shell wrapper that generates a DSC index for a PDF file.

Behavior:

- Accepts `pdffile [dscfile]`; otherwise derives `.dsc` by replacing the input extension.
- Runs Ghostscript no-display and safe with `pdf2dsc.ps`, passing `-sPDFname` and `-sDSCname`, then `-c quit`.

This is a Ghostscript utility launcher for PDF page-index metadata.
