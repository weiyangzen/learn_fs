# File Research: sources/os/bsd/netbsd-src/lib/libutil/Makefile

## Purpose
Build definition for NetBSD `libutil`, collecting utility APIs for login accounting, disk naming, disklabel helpers, mount option parsing, pidfiles, ptys, tty messaging, capability handling, and formatting helpers.

## Key Details
- Builds `LIB=util` with `USE_SHLIBDIR=yes`.
- Pulls shared common utility sources from `${NETBSDSRCDIR}/common/lib/libutil/Makefile.inc`.
- Local source list includes storage-facing helpers such as `getdiskrawname.c`, `getfsspecname.c`, `disklabel_dkcksum.c`, `disklabel_scan.c`, `opendisk.c`, `getmntopts.c`, and disk sysctl helpers.
- Includes `compat/Makefile.inc` for legacy ABI wrappers.
- Sets parser prefix `YPREFIX=__pd` for `parsedate.y`.
- Declares manpages and many `MLINKS` for alternate API names.

## Dependencies and Role
- Central build index for this batch.
- Storage/filesystem relevance is mainly through disklabel, mount option, raw/cooked disk name, and fstab/device-name helper APIs.
