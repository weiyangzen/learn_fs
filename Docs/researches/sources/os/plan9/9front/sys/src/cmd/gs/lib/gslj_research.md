# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gslj

Ghostscript print wrapper for LaserJet output.

Behavior:
- Executes Ghostscript quiet with `-sDEVICE=laserjet -r300 -dNOPAUSE`.
- Uses `gslp.ps`, `-sPROGNAME=$0`, centered `date` heading, and all user arguments.

Filesystem relevance:
- Printer/process wrapper only.
