# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj500

Shell convenience wrapper for printing through Ghostscript’s DeskJet 500 device.

It runs `gs` quietly with:

- `-sDEVICE=djet500`
- `-r300`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
