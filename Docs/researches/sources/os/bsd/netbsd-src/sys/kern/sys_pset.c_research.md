# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_pset.c

## Purpose
Implements processor sets: creation/destruction, CPU assignment, LWP/process binding, kauth policy defaults, and sysctl exposure.

## Main Interfaces
- `psets_init`: allocates the processor-set table and installs a kauth listener.
- `sys_pset_create`, `sys_pset_destroy`: privileged processor-set lifecycle.
- `sys_pset_assign`: assign/query a CPU's processor set.
- `sys__pset_bind`: bind a process or LWP to a processor set.
- `sysctl_psets_max`, `sysctl_psets_list`: manage/report processor-set limits and active IDs.
- Helpers: `psets_realloc`, `psid_validate`, `kern_pset_create`, `kern_pset_destroy`.

## State And Control Flow
Global `psets` is an array of `pset_info_t *` protected by `cpu_lock`, with `psets_max` and `psets_count`. Destroying a set clears matching CPU scheduler state and all LWPs using that set. Assigning a CPU validates the target, prevents removing the last default CPU or assigning offline CPUs incorrectly, rejects conflicts with explicit affinity masks, updates scheduler state, and migrates affected LWPs.

## Dependencies And Integration
Depends on scheduler per-CPU state, global CPU/LWP lists, `cpu_lock`, `proc_lock`, LWP migration, kauth authorization, sysctl, and CPU affinity masks.

## Risks And Edge Cases
- Scheduler may read `l_psid` locklessly, so updates must preserve tolerable transient states.
- Reallocating to a smaller table rejects ranges containing active sets.
- Binding copies out only one old pset ID even when multiple LWPs are affected.
- Assignment must avoid affinity-mask conflicts and bound/intr LWP migration.

## Filesystem Relevance
Indirect. Processor sets affect scheduling of filesystem and I/O workloads but do not implement filesystem state.
