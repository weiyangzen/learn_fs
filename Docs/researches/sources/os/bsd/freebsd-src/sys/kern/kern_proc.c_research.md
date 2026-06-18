# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_proc.c

## Purpose
FreeBSD kernel process-table, process-group, session, process-info export, and whole-system process-stop support. This is a central `sys/kern` implementation file backing PID lookup, `kern.proc.*` sysctls, process/session/job-control bookkeeping, and VM/process metadata reporting.

## Major Responsibilities
- Initializes process-global structures in `procinit()`: PID hash locks, process-group hash, `allproc_lock`, `proctree_lock`, `procid_lock`, `proc_zone`, `pgrp_zone`, and UID hash state.
- Implements type-stable `struct proc` and `struct pgrp` UMA lifecycle hooks: `proc_ctor()`, `proc_dtor()`, `proc_init()`, `proc_fini()`, and `pgrp_init()`.
- Manages PID/process-group/session ID bitmaps with `proc_id_set()`, `proc_id_set_cond()`, and `proc_id_clear()`.
- Provides process lookup helpers: `pfind()`, `pfind_any()`, `pfind_any_locked()`, `pgfind()`, `pget()`, and `proc_iterate()`.
- Handles process-group/session transitions and job-control orphaning through `enterpgrp()`, `enterthispgrp()`, `leavepgrp()`, `pgdelete()`, `killjobc()`, `orphanpg()`, `sess_hold()`, and `sess_release()`.
- Fills user-visible process snapshots in `kinfo_proc` through `fill_kinfo_proc()`, `fill_kinfo_proc_only()`, `fill_kinfo_proc_pgrp()`, `fill_kinfo_thread()`, and `fill_kinfo_aggregate()`.
- Implements `kern.proc` sysctl handlers for process lists, arguments, environment, auxv, executable pathname, ABI name, VM maps, kernel stacks, groups, rlimits, ps strings, umask, OS release, signal trampoline, sigfastblock, and VM layout.
- Implements `stop_all_proc()`, `resume_all_proc()`, and their blocker lock, used by kernel services needing a global stop of user-mode processes.

## Filesystem / VM Relevance
- `proc_get_binpath()` reports a process executable path using `p_textvp`, `p_textdvp`, and `p_binname`. It first tries `vn_fullpath_hardlink()` using the original exec hardlink name, verifies with `namei()`, and falls back to `vn_fullpath()`.
- `kern_proc_vmmap_out()` emits `kinfo_vmentry` records for a process address space, including vnode-backed mappings, vnode attributes, device pager paths, SysV/POSIX shared memory identity, copy-on-write flags, resident counts, and superpage flags.
- `kern_proc_vmmap_resident()` walks VM object backing chains and radix trees to estimate resident pages for map entries, using `pmap_mincore()` to account for superpages.
- Process umask reporting uses `p->p_pd->pd_cmask`; rlimit and executable-path reporting are common inspection hooks used by filesystem tools and procfs-like consumers.

## Locking and Lifetime Model
- `proctree_lock` protects process tree, process groups, sessions, and reaper/job-control relationships.
- PID hash buckets are protected by striped `pidhashtbl_lock[]`; `allproc_lock` protects global process iteration.
- Process state is protected by `PROC_LOCK(p)`; process-group/session state uses `PGRP_LOCK()` and `SESS_LOCK()`.
- `struct proc` and `struct pgrp` zones are `UMA_ZONE_NOFREE`, preserving pointer type stability for concurrent lookup/debug paths.
- Vnode and VM references are explicitly acquired before dropping process or map locks: e.g. `vref()`, `vmspace_acquire_ref()`, `VM_OBJECT_RLOCK()`, and `vn_lock()`.

## Key Interfaces
- Lookup: `pfind()`, `pfind_any()`, `pget()`, `pgfind()`, `proc_iterate()`.
- Process groups/sessions: `enterpgrp()`, `enterthispgrp()`, `leavepgrp()`, `sess_hold()`, `sess_release()`.
- Export: `kern_proc_out()`, `proc_getargv()`, `proc_getenvv()`, `proc_getauxv()`, `proc_get_binpath()`, `kern_proc_vmmap_out()`.
- Sysctl surface: `kern.proc.*` nodes for process table and per-process details.
- Global process quiescing: `stop_all_proc_block()`, `stop_all_proc_unblock()`, `stop_all_proc()`, `resume_all_proc()`.

## Notable Edge Cases
- `pget()` can treat TIDs as process selectors unless `PGET_NOTID` is set.
- `sysctl_kern_proc_args()` uses cached `pargs` when available, otherwise reads `ps_strings` from the target process memory.
- `get_proc_vector()` and 32-bit variant validate argument/environment/auxv vector counts and alignment before copying from target memory.
- VM map export restarts around map timestamp changes so records stay coherent across concurrent address-space modification.
- `stop_all_proc()` deliberately skips kernel/system/traced/exiting processes and loops until no restart conditions remain.
