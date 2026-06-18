# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_fork.c

Read completely: 673 lines.

Implements process creation for `fork(2)`, historical and NetBSD `vfork(2)` variants, Linux-compatible `__clone(2)`, kernel-internal `fork1()`, and the initial child return path. It is the process creation counterpart to `kern_exit.c`.

Entry points and flags:
- `sys_fork()` calls `fork1()` with normal `SIGCHLD` exit signaling.
- `sys_vfork()` uses `FORK_PPWAIT` without shared VM for 4.4BSD/Mach-style compatibility.
- `sys___vfork14()` uses `FORK_PPWAIT | FORK_SHAREVM` for original shared-address-space vfork semantics.
- `sys___clone()` translates Linux clone flags to NetBSD fork flags: VM, cwd, file table, signal actions, and vfork-style parent wait. It rejects unsupported `CLONE_PTRACE`, invalid signal numbers, `CLONE_SIGHAND` without `CLONE_VM`, and `CLONE_FILES` with close-on-fork state.

`fork1()` flow:
- Increments global `nprocs`, enforces `maxproc`, asks kauth for fork authorization, and enforces per-user `RLIMIT_NPROC`, with optional `forkfsleep` delay on limit failures.
- Allocates U-area and proc structure before the commit point; after this, later resource allocation is expected not to fail.
- Initializes the child proc by zeroing/copying prescribed proc regions, sets inherited process flags, emulation, exec switch, locks/CVs, RAS state, text vnode/path, file descriptor table, cwd, limits, vfork parent-wait state, signal actions, scheduler state, stats, VM space, and LWP.
- Supports shared files/cwd/signals/VM and clean file table creation depending on flags.
- Copies/inherits ktrace state when `KTRFAC_INHERIT` is set.
- Calls emulation fork hooks and general fork hooks before publishing the child.
- Under `proc_lock`, inserts the child in the parent list, process group list, and `allproc`, handles ptrace fork/vfork parent changes, updates CPU fork counters, notifies kqueue process filters through `knote_proc_fork()`, and makes the child runnable unless `PS_STOPFORK` is active.
- Returns the child pid to the parent and waits for vfork completion if `FORK_PPWAIT` was requested.

Tracing and vfork:
- `tracefork()`, `tracevfork()`, and `tracevforkdone()` test ptrace event flags and suppress ordinary fork tracing for parent-wait vfork cases as appropriate.
- For traced fork/vfork, the child may be reparented to the tracer via `proc_changeparent()`, flagged `PSL_TRACEDCHILD`, and parent events are delivered through `eventswitch()`.
- The parent waits on `l_waitcv` while `l_vforkwaiting` remains true and optionally emits `PTRACE_VFORK_DONE`.

Child return:
- `child_return()` emits child-side ptrace fork/vfork events with `eventswitchchild()`, calls `md_child_return()`, and records a ktrace syscall return using `SYS_fork` for all fork variants.

Concurrency and integration:
- Process counts use atomics and per-uid accounting through `chgproccnt()`.
- `proc_lock`, per-process locks, scheduler locks, and LWP locks coordinate publication and runnable state.
- Integrates with kauth, uidinfo, filedesc, cwd, limits, UVM, signals, profiling, ktrace, kqueue, ptrace, RAS, emulation hooks, and DTrace process create probes.

Risks and notes:
- Comments call out a racy copy of `p_mqueue_cnt`.
- After the commit point, allocation failures are not expected; pre-commit allocation is deliberately front-loaded.
- Linux clone stack handling passes stack size zero because the Linux ABI leaves stack growth direction to the caller.
