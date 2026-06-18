# File Research: sources/os/bsd/openbsd-src/sys/sys/param.h

Defines global OpenBSD/BSD system constants, machine-independent kernel parameters, filesystem sizing, alignment, bit, rounding, and fixed-point macros.

Key contents:
- Version macros: `BSD`, `BSD4_3`, `BSD4_4`, `OpenBSD`, `OpenBSD7_9`.
- Includes system limits, types, signals, machine limits, and machine parameters.
- Public constants: `MAXCOMLEN`, `MAXINTERP`, `MAXLOGNAME`, `MAXUPRC`, `NCARGS`, `NGROUPS`, `NOFILE`, `NOFILE_MAX`, `NOGROUP`, `MAXHOSTNAMELEN`.
- Kernel sleep priorities and priority flags.
- Device and alignment macros.
- Filesystem constants: `MAXPHYS`, `MAXBSIZE`, `DEV_BSIZE`, block conversion macros, `MAXPATHLEN`, `MAXSYMLINKS`.
- Flag, bitmap, rounding, min/max, `offsetof`, `nitems`, and fixed-point load average macros.

Risk notes:
- This header is included widely; changes affect kernel ABI assumptions, filesystem buffers, path limits, and scheduling constants.
