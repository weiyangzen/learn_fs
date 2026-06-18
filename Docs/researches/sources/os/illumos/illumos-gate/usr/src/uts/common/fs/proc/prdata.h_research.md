# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prdata.h

## Role

Private procfs header for illumos kernel procfs implementation. It defines procfs node/common structures, node types, internal flags, helper macros, usage accounting structures, and prototypes shared across procfs source files.

## Major Responsibilities

- Defines stop-state and alignment helpers used by procfs control/read paths.
- Defines `prcommon_t`, the shared process/lwp object referenced by procfs vnodes.
- Defines `prnode_t`, the per-vnode procfs node object.
- Enumerates all procfs node types, including process files, lwp files, fd/object/path/contract directories, and old procfs compatibility nodes.
- Declares kernel-only procfs helpers used by control, vnode, data, map, page-data, and machine-dependent code.
- Defines the chained procfs I/O buffer interface used to avoid very large single allocations.
- Declares 32-bit procfs conversion/control entry points when enabled.
- Documents machine-dependent xregs support requirements.

## Key Types

- `prcommon_t`: common process/lwp tracking object with wait mutex/CV, flags, writer/self-open counts, pid, data model, process pointer, thread pointer, slot/tid metadata, reference count, and pollhead.
- `prnode_t`: procfs vnode-private object with node type, mode, inode, hat id, common and process-common pointers, parent/child references, real vnode backing pointer for fd/object/path entries, owner, vnode pointer, contract pointer, and template type.
- `prnodetype_t`: node-type enum covering `/proc`, `/proc/self`, pid directories, address space, control/status files, map/xmap/rmap, credentials, sigact, auxv, lwp directories and lwp files, fd/fdinfo/object/path/contract trees, secflags, and legacy nodes.
- `prhusage_t`: internal high-resolution usage structure paralleling `prusage_t` with `hrtime_t` time fields and counters.

## Important Macros And Flags

- `DSTOPPED(t)` identifies a thread stopped due to a directed `/proc` stop.
- `round4`, `round8`, `round16`, and `roundlong` provide ABI-alignment helpers.
- `PRC_DESTROY`, `PRC_LWP`, `PRC_SYS`, `PRC_POLL`, and `PRC_EXCL` describe `prcommon_t` state.
- `PR_INVAL`, `PR_ISSELF`, `PR_AOUT`, and `PR_OFFMAX` describe per-node state.
- `VTOP()` and `PTOV()` convert between vnodes and procfs nodes.
- `PROCESS_NOT_32BIT()` is used by ILP32 procfs control paths to reject non-32-bit targets.

## Declared Interfaces

The header exports procfs internals including:

- Locking and lifetime: `pr_p_lock()`, `prlock()`, `prunlock()`, `prunmark()`, `prgetnode()`, `prfreenode()`.
- Control: `prwritectl()`, `prwritectl32()`, `pr_stop()`, `pr_wait_stop()`, `pr_setrun()`, `pr_wait_die()`, `allsetrun()`.
- Signal/fault/syscall tracing: `pr_setsig()`, `pr_kill()`, `pr_unkill()`, `pr_setentryexit()`, `pr_sethold()`, `pr_setfault()`.
- File/address-space helpers: `pr_getf()`, `pr_releasef()`, `prusrio()`.
- Maps and page data: `prgetmap()`, `prgetxmap()`, `prpdread()`, old procfs variants, and 32-bit variants.
- Usage/action conversion: `prgetusage()`, `praddusage()`, `prcvtusage()`, `prgetaction()`.
- Watchpoints: `set_watched_area()`, `clear_watched_area()`, `pr_free_watchpoints()`, `pr_cancel_watch()`.
- Machine-dependent register and xregs routines.

## Xregs Contract

The extended-register comment block is an important interface contract. It states that `prxregset_t` is opaque and variable-sized, and requires machine-dependent code to provide support detection, size calculation, write minimum sizing, write full sizing, read, and validated write operations. It explicitly warns that xregs write buffers may be unaligned because both ILP32 and LP64 procfs controls share the mechanism.

## Research Notes

This header defines the internal vocabulary used by `prcontrol.c` and the rest of procfs. Its most important architectural role is separating common process/lwp state (`prcommon_t`) from individual vnode nodes (`prnode_t`) while exposing enough internal helpers for procfs control, status, vnode, and machine-dependent implementations.
