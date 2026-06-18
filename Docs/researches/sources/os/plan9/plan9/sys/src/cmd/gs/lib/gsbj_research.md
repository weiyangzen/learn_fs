# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsbj

Shell convenience wrapper for printing through Ghostscript’s Canon BJ-10e device.

It runs `gs` quietly with:

- `-sDEVICE=bj10e`
- `-r180`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
