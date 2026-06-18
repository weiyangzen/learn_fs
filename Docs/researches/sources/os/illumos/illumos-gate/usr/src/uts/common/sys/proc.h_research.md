# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/proc.h

## Purpose
Defines the central kernel process structure, process/LWP directory state, PID state, process flags, signal/process-management macros, and many kernel process/thread/LWP/signal function prototypes.

## Main Interfaces
- Profiling and context:
  - `struct prof`
  - `lwpent_t`
  - `pctxop_t`
  - `lwpdir_t`
  - `tidhash_t`
  - `ret_tidhash_t`
- `proc_t`: central process object containing address space, credentials, parent/child/session/PID links, locks/condition variables, signal state, LWP/thread directories, `/proc` state, watchpoints, stack/page-size state, microstate/resource accounting, profiling, door state, audit state, LDT state on x86, timers, task/project/pool/zone/brand/security/resource-control state, event-port count, upanic state, and embedded `struct user`.
- Kernel globals:
  - `practive`
  - `proc_sched`
  - `proc_init`
  - `proc_pageout`
  - `proc_fsflush`
  - `p0`, `p0lock`, `pid0`
- UID process counts:
  - `struct upcount`
- PID support:
  - `struct pid`
  - `p_pgrp`, `p_pid`, `p_slot`, `p_detached`
  - `PID_HOLD`, `PID_RELE`
  - `PID_ALLOC_PROC`
- Persistent lock:
  - `struct plock`
  - `p_lock` macro.
- Process states:
  - `SSLEEP`, `SRUN`, `SZOMB`, `SSTOP`, `SIDL`, `SONPROC`, `SWAIT`
- Child notification and process flags:
  - `CLDPEND`, `CLDCONT`, `CLDNOSIGCHLD`, `CLDWAITPID`
  - `/proc` flags `P_PR_*`
  - process flags `SSYS`, `SEXITING`, `SFORKING`, `SWATCHOK`, `SKILLED`, `SEXECED`, `SMSACCT`, `SDOCORE`, and others.
  - pool flags `PBWAIT`, `PEXITED`
  - upanic flags `P_UPF_*`
- Signal/process macros:
  - `PTOU`
  - `tracing`
  - `ISSIG`, `ISSIG_FAST`, `ISSIG_PENDING`
  - `ISSTOP`, `ISHOLD`, `MUSTRETURN`, `pr_watch_active`
- Constants/types:
  - `FORREAL`, `JUSTLOOKING`
  - `SUSPEND_NORMAL`, `SUSPEND_PAUSE`
  - `NOCLASS`, `CLASS_UNUSED`
  - `lwp_stat_id_t`
  - `prkillinfo_t`
- Kernel prototypes for:
  - process lifecycle and VM release
  - signals and signal queues
  - PID lookup/allocation/group/session helpers
  - microstate accounting
  - thread creation/context/TSD
  - LWP lifecycle, hold/run/continue/fork/register handling
  - signal queue allocation, delivery, and wait-status conversion.

## Dependencies And Relationships
Includes thread, credentials, user, watchpoint, timers, model, refstr, AVL/list, rctl, doors, signalfd, and security flags. It is one of the central kernel headers used by process management, `/proc`, signals, scheduling, resource controls, zones, brands, doors, and pools.

## Research Notes
Many `proc_t` fields are grouped by lock ownership in comments: no explicit lock, `pidlock`, `p_lock`, `as_rangelock`, dedicated locks, and subsystem locks. The first two fields of related project structs and lock macros elsewhere depend on stable layout conventions.
