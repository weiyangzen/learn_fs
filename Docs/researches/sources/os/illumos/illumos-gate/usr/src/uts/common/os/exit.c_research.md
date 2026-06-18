# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exit.c

## Purpose

`exit.c` implements process termination, zombie creation, child wait status collection, process table detachment, resource/accounting cleanup, and special handling for zone init restart or shutdown. It is the counterpart to `exec.c` in process lifecycle management.

## Main Entry Points

- `rexit()` (`exit.c:137`) implements the simple exit syscall wrapper by calling `exit(CLD_EXITED, rval)`.
- `exit()` (`exit.c:317`) calls `proc_exit()` and, if another LWP already owns process exit, falls into `lwp_exit()`.
- `proc_exit()` (`exit.c:462`) is the full process-exit state machine.
- `waitid()` (`exit.c:1055`) implements wait semantics over child process state.
- `freeproc()` (`exit.c:1342`) frees zombie process state after the parent has accepted it or the process evaporates.

## Wait Status Helpers

`wstat()` converts `CLD_*` code/data pairs into traditional wait status bits. `exit_reason()` formats a short diagnostic string for zone init failure/restart messages. `winfo()` fills kernel `siginfo` for wait operations and optionally clears wait state and `CLDPEND`.

## Zone Init Restart Handling

`restart_init()` (`exit.c:155`) is called when a zone’s init exits but policy says it should be restarted. It logs the reason, cleans file descriptors with `pollcleanup()` and `closeall()`, resets process flags, signal state, queued signal info, current/root directories, cwd refstr, secflags, credentials, and controlling tty. It then calls `exec_init()` for the zone init path.

`zone_init_exit()` (`exit.c:352`) decides whether to restart, reboot, halt, or proceed with normal exit when the zone init exits. It considers boot errors, zone/global shutdown state, `zone_restart_init`, `zone_reboot_on_init_exit`, and `zone_restart_init_0`.

This path is unusual because successful restart returns through the normal syscall path rather than continuing process teardown.

## Process Exit Flow

`proc_exit()` first marks the process exiting with `proc_is_exiting()`, calls `exitlwps()` to remove other LWPs, accounts remaining process ticks to the task, fires DTrace exit probes, and clears brand state.

If the process is the zone init, `zone_init_exit()` may restart it and return. Otherwise the function proceeds with teardown:

- Calls `lwp_pcb_exit()`.
- Allocates a `sigqueue_t` for `SIGCLD` unless the process will evaporate.
- Revokes doors, releases schedctl state, waits for AIO cleanup, destroys lwpchan cache, cleans DTrace helpers and signalfd state.
- Removes interval timers, alarm timeout, realtime profile cyclics, and upanic state.
- Runs `pollcleanup()` before descriptor closure.
- Enters `p_lock`, cleans DTrace probes, cancels `p_itimerid`, runs `lwp_cleanup()`, enters pool barrier, blocks `/proc` via `prbarrier()`, clears pending signals and signal info, marks current thread `TP_LWPEXIT`, removes LWP hash state, calls `prexit()`, sets `p_lwpcnt = 0`, clears thread list, frees sigqueues, terminates microstate accounting, and detaches executable vnode pointers.

After dropping `p_lock`, it frees watched pages, closes all files, releases controlling tty, frees SPARC utraps, exits SysV semaphore state, performs accounting/audit/exacct, frees address space with `relvm()`, closes/releases `p_exec`, releases `p_execdir`, exits contracts, leaves process contracts, and removes pool association.

## Parent/Child and Zombie State

Under `pidlock`, `proc_exit()` removes the exiting process from the parent’s newstate list, reassigns orphan relationships to next-of-kin, reparents children to `proc_init`, kills ptraced reparented children, and posts state for zombie children as needed.

It then aggregates task and child resource usage, sets `p_stat = SZOMB`, clears ptrace compatibility flag, stores wait data/code, snapshots cwd/root/cwd refstr references for later release, frees resource controls, decrements task/project/zone LWP counters, clears LWP directory/hash structures, runs process-context exit hooks, and temporarily points `curthread` at `zsched` or `p0` so zone references remain valid while the process may be freed.

If not evaporating, `sigcld()` notifies the parent. If evaporating, it mimics ignored `SIGCHLD`, broadcasts `p_srwchan_cv`, and immediately calls `freeproc()`.

Finally it releases cwd/root/cwd references, moves the thread to `p0`, frees LWP directory/hash memory including retired hash tables, and calls `thread_exit()`.

## Wait Implementation

`waitid()` validates options and id type, strips obsolete `_WNOCHLD`, and scans child state under `pidlock`.

It optimizes the common `P_ALL | WNOHANG | WEXITED` case by checking `p_child_ns`. The main loop first scans `p_child_ns` for exited/dumped/killed children, respecting `CLDWAITPID` and `WNOWAIT`. If a waitable child is found, it fills `siginfo`, optionally frees the process, drops `pidlock`, and updates SIGCLD bookkeeping.

If no child on the newstate list qualifies, it scans all children for trapped/stopped/continued states and validates stopped state with `jobstopped()`. It returns `ECHILD`, zeroed `siginfo` for `WNOHANG`, or waits interruptibly on the parent condition variable.

`waitsys()` and `waitsys32()` are syscall wrappers that copy out native or 32-bit siginfo.

## Process Freeing

`freeproc()` assumes a zombie with no thread list under `pidlock`. It clears remaining signal queues, informs `/proc` with `prfree()`, preserves `proc_init`, decrements per-uid process count, frees credentials and core-control references, propagates child CPU/accounting/resource usage to next-of-kin when appropriate, removes orphan links, detaches task/project membership, detaches from parent child lists, releases pid/proc memory through `pid_exit()`, and releases the task.

`proc_detach()` removes a process from its parent’s child list and newstate list. `delete_ns()` and `add_ns()` maintain the parent newstate list.

## External Interactions

This file coordinates with:

- `exec.c`: `restart_init()` uses `exec_init()` after resetting state.
- Descriptor management in `fio.c`: `closeall()` and poll cleanup.
- VFS/vnodes: executable/current/root directory reference release and close.
- VM: `relvm()`.
- Process contracts, tasks, projects, zones, pools, and resource controls.
- `/proc`, DTrace, audit, exacct, accounting, signal and wait subsystems.

## Research Notes

The important invariants are single-LWP ownership of process exit, the `pidlock` ordering around child lists and zombie state, delayed release of cwd/root until after `SZOMB`, and careful `curthread->t_procp` reassignment so late vnode/task releases still have a valid zone context.
