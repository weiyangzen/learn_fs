# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gsbj

Ghostscript print wrapper for Canon BubbleJet BJ-10e style output.

Behavior:
- Executes Ghostscript quiet with `-sDEVICE=bj10e -r180 -dNOPAUSE`.
- Sets `-sPROGNAME=$0` and runs `gslp.ps`.
- Adds a centered heading containing `date`, then forwards all user arguments.

Filesystem relevance:
- Printer/process wrapper only.
