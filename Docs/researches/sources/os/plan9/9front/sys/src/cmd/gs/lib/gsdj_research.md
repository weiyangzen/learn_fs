# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gsdj

Ghostscript print wrapper for DeskJet output.

Behavior:
- Executes Ghostscript quiet with `-sDEVICE=deskjet -r300 -dNOPAUSE`.
- Runs `gslp.ps` with `-sPROGNAME=$0`, a centered date heading, and all user arguments.

Filesystem relevance:
- Printer/process wrapper only.
