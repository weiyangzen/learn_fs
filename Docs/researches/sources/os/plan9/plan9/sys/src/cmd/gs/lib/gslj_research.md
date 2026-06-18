# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslj

Shell convenience wrapper for printing through Ghostscript’s LaserJet device.

It runs `gs` quietly with:

- `-sDEVICE=laserjet`
- `-r300`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
