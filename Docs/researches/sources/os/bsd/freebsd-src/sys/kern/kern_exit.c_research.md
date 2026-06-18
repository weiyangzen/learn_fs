# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_exit.c

Read status: complete file reviewed.

This file implements process exit, asynchronous syscall-exit handling, abort logging, wait/wait6/pdwait, zombie reaping, reparenting, reaper subtree cleanup, orphan tracking for ptrace, and process-parent notification.

Main entry points include `sys__exit`, `kern_exit`, `exit1`, `exit_onexit`, `proc_set_p2_wexit`, `sys_abort2`, `kern_abort2`, `sys_wait4`, `sys_wait6`, `sys_pdwait`, `kern_wait`, `kern_wait6`, `kern_pdwait`, `proc_reap`, `proc_reparent`, `proc_add_orphan`, `proc_clear_orphan`, `proc_realparent`, and `reaper_abandon_children`.

`kern_exit` handles the normal syscall path and the ptrace remote syscall case. If `TDB_SCREMOTEREQ` is active it stores the desired exit status/signal, marks `P_ASYNC_EXIT`, and schedules `TDA_ASYNC_EXIT`; otherwise it calls `exit1` directly. `initexit` registers the async-exit AST handler.

`exit1` is the full process teardown path. It protects init from accidental death, clears kernel AST cleanup, marks write-exit flags, single-threads and terminates other threads, stores exit code/signal, drains limit callouts, audits the exit, kills task peers for task leaders, runs process-exit event handlers, stops profiling and interval timers, calls ABI exit hooks, releases sigio ownership, frees procdesc and filedesc tables, removes peer links, releases VM resources and accounting, drops text vnode/binname references, frees limits, removes the process from allproc and prison lists, reparents children and orphans, emits DTrace/kqueue exit notifications, handles procdesc exit suppression of parent signals, queues SIGCHLD or custom parent signal, flushes signal queues, transitions to `PRS_ZOMBIE`, accumulates child rusage, and calls `thread_exit`.

Wait handling is centered on `kern_wait6`. `wait6_checkopt` validates flags, `proc_to_reap` filters children by id type and options, and `wait6_check_alive` reports traced, stopped, or continued live children. `proc_reap` finalizes zombies: it supports `WNOWAIT`, moves ptraced children back to their real parent when appropriate, removes pid hash and sibling links, clears reaper/orphan state, leaves process groups, detaches the process knlist, folds rusage into the waiting parent, releases RACCT state, credentials, pargs, sigacts, threads, VM/machine resources, MAC state, and drops the process-tree reference.

`kern_pdwait` mirrors wait semantics for process descriptors. It validates rights with `cap_pdwait_rights`, uses the procdesc's process pointer under `proctree_lock`, supports live stopped/trapped/continued reporting, reaps zombies, and sleeps on the procdesc channel when blocking.

Reparenting and reaper logic maintain parent, original-parent, orphan, and reaper-subtree invariants. `proc_realparent` resolves ptrace/orphan cases, `proc_reparent` moves children between parent lists and queues pending child status to the old parent, and `reaper_abandon_children` moves a dying reaper's subtree to its own reaper. `proc_clear_orphan` preserves `P_TREE_FIRST_ORPHAN` markers.

`kern_abort2` logs bounded user-provided reason text and up to 16 pointer arguments, then exits with SIGABRT on valid input or SIGKILL when user data is inaccessible. Compatibility `owait` routes to `kern_wait`.

Sysctls include `kern.kill_on_debugger_exit`, controlling whether traced children are killed when a debugger exits, and `kern.wait_dequeue_sigchld`, controlling SIGCHLD dequeue behavior when waiting on live process events.

Risk areas are lock ordering across `proctree_lock`, `allproc_lock`, proc locks, and pgrp/session locks; lost wakeups around zombie transition; ptrace orphan/reparent edge cases; procdesc exit races; async exit reentry; resource accounting exactly once; and preserving child waitability while preventing stale process references.
