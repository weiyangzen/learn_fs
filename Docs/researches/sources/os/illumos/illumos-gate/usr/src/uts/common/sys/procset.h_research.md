# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procset.h

## Purpose
Defines process-set identifiers and set-combination operations used by signal, priority, wait, and event-exit interfaces.

## Main Interfaces
- Initial identifiers:
  - `P_INITPID`
  - `P_INITUID`
  - `P_INITPGID`
- `idtype_t`: identifies process sets by PID, PPID, PGID, SID, scheduling class, UID, GID, all, LWP ID, task, project, pool, zone, contract, CPU, or processor set.
- `idop_t`: set operations `POP_DIFF`, `POP_AND`, `POP_OR`, `POP_XOR`.
- `procset_t`: left/right simple set plus set operator.
- `setprocset()`: initialization macro.
- Kernel helpers:
  - `dotoprocs()`
  - `dotolwp()`
  - `procinset()`
  - `sigsendproc()`
  - `sigsendset()`
  - `cur_inset_only()`
  - `getmyid()`

## Dependencies And Relationships
Includes feature tests, types, and signal definitions. Used by `sigsend`, `priocntl`, `waitid`, and related system calls. Some names are hidden under strict XPG namespace conditions.

## Research Notes
The comments define `POP_AND` as “set disjunction” and `POP_OR` as “set conjunction,” but their described behavior is intersection and union respectively.
