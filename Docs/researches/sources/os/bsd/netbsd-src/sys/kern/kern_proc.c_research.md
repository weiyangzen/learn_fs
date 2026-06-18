# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_proc.c

## Purpose

`kern_proc.c` is the central NetBSD kernel implementation for process identity, process lists, PID/LWP lookup, process group/session membership, process-specific storage, process credential propagation support, and `kern.proc*` sysctl process reporting. It is not filesystem code directly, but it is foundational for VFS-facing process context: current working directory reporting, executable pathname reporting, credential visibility checks, process rlimits, and process references used by other kernel subsystems.

## Main Responsibilities

- Maintains global process lists:
  - `allproc` for active processes.
  - `zombproc` for zombies.
  - `proc_lock` as the global process list/session/PID-table lock.
  - `proc_psz` for pserialize-protected PID table memory replacement.
- Implements the PID table:
  - `struct pid_table` maps PID/LID slots to either an LWP, a process placeholder, or a free slot.
  - Low pointer bits encode slot state: free, process, LWP.
  - `expand_pid_table()` doubles the table and waits for pserialize readers before freeing the old table.
- Initializes `proc0`, `session0`, `pgrp0`, `cwdinfo`, limits, vmspace, filedesc, signal state, and credentials.
- Allocates and frees processes/PIDs/LWP IDs.
- Implements process group and session membership:
  - `proc_enterpgrp()`
  - `proc_leavepgrp()`
  - `pgrp_find()`
  - `pg_delete()`
  - `fixjobc()`
  - orphaned process group handling.
- Provides process lookup helpers:
  - `proc_find()`
  - `proc_find_lwpid()`
  - `proc_find_lwp()`
  - `proc_find_lwp_unlocked()`
  - `proc_find_lwp_acquire_proc()`
  - `proc_find_locked()`
- Supports process credential updates:
  - `proc_crmod_enter()`
  - `proc_crmod_leave()`
- Provides process-specific data key/container helpers.
- Implements process visibility authorization listener logic for `KAUTH_SCOPE_PROCESS`.
- Implements `kern.proc`, `kern.proc2`, and `kern.proc_args` sysctl trees.

## Important Data Structures and State

- `struct pid_table`
  - `pt_slot`: encoded process/LWP/free slot.
  - `pt_pgrp`: process group occupying the PID namespace slot.
  - `pt_pid`: actual PID/LID stored in this table slot.
- `pid_table`, `pid_tbl_mask`, `pid_alloc_lim`, `pid_alloc_cnt`, `next_free_pt`, `last_free_pt`, `pid_max`
  - Together implement PID allocation, reuse spacing, table growth, and free-list maintenance.
- `proc0`
  - Static process zero with one LWP, system flags, base session/pgrp, filedesc, cwdinfo, plimit, vmspace, pstats, and sigacts.
- `kern_expose_address`
  - Sysctl-controlled policy for whether kernel addresses are exposed in process reporting. Defaults off under KASLR and on otherwise.

## Initialization Flow

- `procinit()`:
  - Initializes process lists and `proc_lock`.
  - Creates `proc_psz`.
  - Allocates initial PID table.
  - Reserves PID 1 for init.
  - Creates process-specific-data domain.
  - Creates `proc_cache`.
  - Registers the process kauth listener.
- `procinit_sysctl()`:
  - Registers `security.expose_address`.
  - Registers `kern.proc`, `kern.proc2`, and `kern.proc_args`.
- `proc0_init()`:
  - Initializes locks, condition variables, proc0/lwp0 linkage, credentials, cwd lock, limits, file descriptors, kernel vmspace, and signal state.

## PID and LWP Lookup

PID lookup is optimized around direct indexing rather than list walks:

- PID table index is `pid & pid_tbl_mask`.
- LWP lookup can run under pserialize with careful ordering:
  - load mask first;
  - load table pointer second;
  - load slot;
  - validate slot type and process/LID identity.
- `proc_find_lwp()` requires `p->p_lock`.
- `proc_find_lwp_unlocked()` runs in a pserialize read section and returns the LWP locked if valid.
- `proc_find_internal()` filters raw PID table matches to active/stopped processes for ordinary lookup.
- LWP IDs can temporarily occupy the process PID slot; when the first LWP exits, `proc_free_lwpid()` converts the slot back to a process placeholder.

## Process Allocation and Freeing

- `proc_alloc()` gets a process from `proc_cache`, marks it `SIDL`, initializes specific data and DTrace state, then reserves a PID slot.
- `proc_alloc_pid_slot()`:
  - expands PID table if allocation pressure exceeds `pid_alloc_lim`;
  - preserves PID 1 for first user process;
  - allocates from the free list;
  - keeps PID values cycling through a wide enough range.
- `proc_alloc_lwpid()`:
  - usurps the process PID slot for the first LWP when possible;
  - otherwise allocates a separate LWP ID.
- `proc_free_pid_internal()` and wrappers return slots to the free list, unless a process group still pins the PID namespace slot.
- `proc_free_mem()` destroys DTrace process state and returns the object to the pool cache.

## Process Groups and Sessions

- `proc_enterpgrp()` enforces POSIX session/process-group rules for `setsid`, `setpgid`, and spawn paths:
  - only child/self under allowed circumstances;
  - same session checks;
  - child must not have execed;
  - session leaders cannot change groups except no-op;
  - new process groups must use the process PID as pgid;
  - cannot attach to zombie pgrp.
- New sessions allocate `struct session`, clear controlling-terminal state, copy login name while clearing `S_LOGIN_SET`.
- `fixjobc()` maintains terminal job-control eligibility counts.
- `orphanpg()` sends `SIGHUP` and `SIGCONT` to stopped processes in orphaned groups.
- `pg_delete()` detaches controlling tty pgrp references and frees pgrp/session structures when last references drop.

## Credential Update Support

- `proc_crmod_enter()`:
  - resets custom core name to default if credentials are about to change;
  - locks the process;
  - updates current LWP cached credentials from process credentials.
- `proc_crmod_leave()`:
  - swaps in new process credentials;
  - marks sibling LWPs with `LW_CACHECRED` and forces userret refresh;
  - optionally marks `PK_SUGID`;
  - releases/free old credentials after dropping `p_lock`.

This is used by ID-changing syscalls in `kern_prot.c`.

## Sysctl Process Reporting

- `sysctl_doeproc()` backs both legacy `KERN_PROC` and newer `KERN_PROC2`.
- It iterates zombies first, then active processes, to avoid duplicate reporting during process death/list movement.
- It checks `KAUTH_PROCESS_CANSEE` before exposing process entries.
- It supports filters:
  - all processes;
  - PID;
  - process group;
  - session;
  - controlling tty;
  - effective/real UID;
  - effective/real GID.
- It uses `p_reflock` for live process stability and a marker process for zombie/list iteration stability.
- Output helpers:
  - `fill_proc()` copies `struct proc`, scrubbing or conditionally exposing kernel pointers.
  - `fill_eproc()` fills legacy extended process info.
  - `fill_kproc2()` fills modern `kinfo_proc2`, including credentials, signal state, vm size, active LWP state, CPU ID, resource usage, session/tty info, and optional kernel addresses.

## Process Arguments, CWD, Pathname, and Auxv

- `sysctl_kern_proc_args()` handles:
  - `KERN_PROC_ARGV`
  - `KERN_PROC_NARGV`
  - `KERN_PROC_ENV`
  - `KERN_PROC_NENV`
  - `KERN_PROC_PATHNAME`
  - `KERN_PROC_CWD`
- `copy_procargs()`:
  - reads `ps_strings`;
  - resolves argv/env vector addresses;
  - copies user strings page by page via the target vmspace;
  - handles modified argv arrays with NULL entries as graceful termination;
  - supports 32-bit compat hooks.
- `fill_pathname()` returns `p->p_path` if available.
- `fill_cwd()` locks the process cwdinfo and uses `getcwd_common()` to format the current directory path.
- `proc_getauxv()` locates auxv after the env pointer array and copies it from the process address space.

## Security and Address Exposure

- `proc_listener_cb()` allows/denies process visibility subrequests:
  - arguments and general entries are broadly allowed by this listener.
  - environment visibility requires UID/saved UID match.
  - kernel pointer visibility depends on `kern_expose_address` and `PK_KMEM`.
- `sysctl_security_expose_address()` requires `KAUTH_SYSTEM_KERNADDR` authorization and only accepts values `0`, `1`, or `2`.
- `get_expose_address()` asks kauth whether kernel pointers may be exposed for a process.

## Concurrency Notes

- `proc_lock` protects global process lists, PID table logical updates, process groups, and sessions.
- `p->p_lock` protects per-process mutable fields and LWP list stability in many paths.
- `p_reflock` prevents process teardown while sysctl readers inspect process state.
- pserialize protects unlocked PID table readers while `expand_pid_table()` replaces table memory.
- `tty_lock` interlocks process group changes with tty reads/control-terminal state.
- Credential changes use process lock plus per-LWP locking for cache invalidation.
