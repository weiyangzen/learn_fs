# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/param.h

## Purpose
Defines legacy and central system parameters used across kernel and user code: path/name limits, user/group constants, block and page conversion macros, file and process limits, machine-dependent exported parameters, and POSIX configuration defaults.

## Main Interfaces
- TTY and POSIX compatibility constants:
  - `_POSIX_VDISABLE`
  - `_TTY_BUFSIZ`
  - `MAX_INPUT`, `MAX_CANON`, `CANBSIZ`
- User/group constants:
  - `UID_NOBODY`, `GID_NOBODY`, `UID_UNKNOWN`, `GID_UNKNOWN`, `UID_DLADM`, `UID_NETADM`, `GID_NETADM`, `GID_TTY`, `UID_NOACCESS`
  - `MAXUID`, `MAXPROJID`, `MINEPHUID`
- Kernel PID constants:
  - `MAX_TASKID`, `MAX_MAXPID`, `DEFAULT_MAXPID`, `DEFAULT_JUMPPID`
  - famous PID values for sched/init/pageout/fsflush
- Filesystem/path constants:
  - `MAXPATHLEN`
  - `TYPICALMAXPATHLEN`
  - `MAXSYMLINKS`
  - `MAXNAMELEN`
  - `MAXLINKNAMELEN`
  - `MAXLINK`
  - `PIPE_BUF`, `PIPE_MAX`
- Block and storage constants:
  - `NBPSCTR`
  - `UBSIZE`
  - `SCTRSHFT`
  - `MAXBSIZE`
  - `DEV_BSIZE`
  - `DEV_BSHIFT`
  - `MAXFRAG`
- Offset and argument-size limits:
  - `MAXOFF32_T`
  - `MAXOFF_T`
  - `MAXOFFSET_T`
  - `NCARGS32`, `NCARGS64`, `NCARGS`
- Conversion macros:
  - `btodb()`, `dbtob()`
  - `lbtodb()`, `ldbtob()`
  - `mmu_ptob()`, `mmu_btop()`, `mmu_btopr()`
  - `mmu_ptod()`, `ptod()`
  - `ptob()`, `btop()`, `btopr()`
  - `dtop()`, `dtopt()`
  - `kbtop()`, `ptokb()`
- Machine-dependent exported variables/macros in kernel/boot contexts:
  - `PAGESIZE`, `PAGESHIFT`, `PAGEOFFSET`, `PAGEMASK`
  - `MMU_PAGESIZE`, `MMU_PAGESHIFT`, `MMU_PAGEOFFSET`, `MMU_PAGEMASK`
  - `KERNELBASE`, `USERLIMIT`, `USERLIMIT32`, `DEFAULTSTKSZ`, `NCPU`, `NCPU_LOG2`, `NCPU_P2`
- Userland sysconf-backed macros:
  - `HZ`, `TICK`, `PAGESIZE`, `PAGEOFFSET`, `PAGEMASK`, `MAXPID`, `MAXEPHUID`

## Dependencies And Relationships
Includes core type, ISA, null, unistd, and optional `machparam.h` definitions. Many kernel and filesystem headers rely on these constants for ABI-sized buffers and address/page math.

## Research Notes
This is a compatibility-heavy public header. Some values are intentionally historical rather than actual implementation limits, such as `MAX_INPUT`, `MAX_CANON`, and `NOFILE`.
