# File Research: sources/os/bsd/netbsd-src/sys/sys/param.h

## Purpose
Provides core NetBSD system parameters, version macros, kernel/user constants, alignment and rounding helpers, filesystem/path limits, scheduler priority constants, stack macros, and kernel sizing defaults.

## Main API
- Version identifiers: `BSD`, `BSD4_3`, `BSD4_4`, `__NetBSD_Version__`, `__NetBSD_Prereq__`, historical `NetBSD`.
- Kernel mode tags: `_HARDKERNEL`, `_SOFTKERNEL`.
- Limits: `MAXCOMLEN`, `MAXINTERP`, `MAXLOGNAME`, `NCARGS`, `NGROUPS`, `NOFILE`, `MAXUPRC`, `MAXHOSTNAMELEN`.
- Utility macros: `MIN`, `MAX`, `ALIGN`, `ALIGNED_POINTER`, `ALIGNED_POINTER_LOAD`, `ACCESSIBLE_POINTER`, `setbit`, `clrbit`, `isset`, `isclr`, `howmany`, `roundup`, `rounddown`, `roundup2`, `rounddown2`, `powerof2`.
- Device/block conversions: `DEV_BSHIFT`, `DEV_BSIZE`, `ctod`, `dtoc`, `ctob`, `btoc`, `dbtob`, `btodb`.
- Filesystem/path constants: `MAXBSIZE`, `MAXFRAG`, `MAXPATHLEN`, `MAXSYMLINKS`, `KERNEL_NAME_MAX`.
- Scheduling priorities: legacy `P*` priorities, `PRI_*`, soft interrupt and kernel thread priorities.
- Kernel helpers: `mstohz`, `hztoms`, `hz2bintime`.

## Dependencies
Includes `sys/null.h`, integer/types headers, system limits, machine parameters and limits, signal definitions, and kernel-only resource/ucred/uio/UVM headers.

## Risks and Notes
This is one of the broadest dependency roots in the kernel. `roundup2`/`rounddown2` are deliberately written to avoid type-width truncation. Many constants are ABI- or compatibility-sensitive and should not be casually changed.
