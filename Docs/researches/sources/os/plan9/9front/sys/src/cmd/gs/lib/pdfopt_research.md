# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pdfopt

Shell wrapper for optimizing PDFs through Ghostscript `pdfopt.ps`.

Behavior:
- Starts with `-dSAFER -dDELAYSAFER` and appends leading options.
- Requires exactly `input.pdf output.pdf`.
- Runs Ghostscript quiet with `-dNODISPLAY`, options, and `pdfopt.ps`.

Filesystem relevance:
- File conversion wrapper only.
