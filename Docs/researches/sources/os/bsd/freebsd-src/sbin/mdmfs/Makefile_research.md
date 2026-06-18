# File Research: sources/os/bsd/freebsd-src/sbin/mdmfs/Makefile

## Summary
Builds the `mdmfs` runtime utility and installs compatibility links/manual aliases for `mount_mfs`.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mdmfs`.
- Adds link `${BINDIR}/mount_mfs`.
- Adds manual cross-link `mdmfs.8 mount_mfs.8`.
- Includes `bsd.prog.mk`.

## Research Notes
The link reflects `mdmfs` acting as the replacement wrapper for the historical `mount_mfs` interface.
