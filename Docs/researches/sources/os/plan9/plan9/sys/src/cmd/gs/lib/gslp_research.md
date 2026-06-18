# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslp

Shell convenience wrapper for printing through Ghostscript’s Epson device.

It runs `gs` quietly with:

- `-sDEVICE=epson`
- `-r180`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
