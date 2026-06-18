# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gsdj500

Ghostscript print wrapper for DeskJet 500 output.

Behavior:
- Executes Ghostscript quiet with `-sDEVICE=djet500 -r300 -dNOPAUSE`.
- Runs `gslp.ps` with program name, centered date heading, and forwarded arguments.

Filesystem relevance:
- Printer/process wrapper only.
