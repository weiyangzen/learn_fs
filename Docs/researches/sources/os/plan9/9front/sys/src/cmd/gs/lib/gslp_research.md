# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gslp

Ghostscript print wrapper for Epson-style output.

Behavior:
- Executes Ghostscript quiet with `-sDEVICE=epson -r180 -dNOPAUSE`.
- Runs `gslp.ps` with program name, centered date heading, and forwarded arguments.

Filesystem relevance:
- Printer/process wrapper only.
