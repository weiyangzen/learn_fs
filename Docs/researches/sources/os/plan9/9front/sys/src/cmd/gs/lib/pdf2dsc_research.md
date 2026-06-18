# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pdf2dsc

Shell wrapper for generating a DSC index from a PDF using Ghostscript `pdf2dsc.ps`.

Behavior:
- Accepts `pdffile [dscfile]`; more than two arguments triggers usage.
- Defaults output to the input basename with `.dsc`.
- Runs Ghostscript quiet, no display, safer modes, with `-sPDFname` and `-sDSCname`, then `pdf2dsc.ps -c quit`.

Filesystem relevance:
- File conversion/index wrapper only.
