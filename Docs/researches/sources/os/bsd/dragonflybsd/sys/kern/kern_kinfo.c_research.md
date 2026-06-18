# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kinfo.c

## Role

Fills `kinfo_proc` and `kinfo_lwp` structures for kernel and libkvm consumers. It translates live or zombie `proc`, `lwp`, and kernel-thread state into stable exported process information, including credentials, process groups, sessions, controlling terminals, VM sizes, jail id, rusage, scheduling state, and wait channels.

## Major Entry Points

- `fill_kinfo_proc(struct proc *p, struct kinfo_proc *kp)` zeroes and fills process-level fields. Caller must hold `p->p_token`.
- `fill_kinfo_lwp(struct lwp *lwp, struct kinfo_lwp *kl)` fills or aggregates LWP-level fields into an existing structure.
- `fill_kinfo_proc_kthread(struct thread *td, struct kinfo_proc *kp)` creates synthetic process/LWP information for kernel threads without a user process.

## Process Data Exported

- Process address, fd table pointer, flags, state, lock/acct/trace flags, signal masks, start time, command name, pid/ppid, process group/session/job-control data, controlling tty device and foreground pgrp/session ids, exit status, thread count, nice value, swap time, VM map size, resident count, text/data/stack sizes, jail id, self rusage, and child rusage.
- Credentials include uid, groups, ruid/svuid, rgid/svgid, and a copied subset of capability bits.
- Null checks protect zombied/deallocating process fields such as pgrp, session, ucred, sigacts, vmspace, parent pointer, and tty state.

## LWP and Kernel Thread Data Exported

- LWP pid/tid, flags, state, lock, thread flags, MP lock count, scheduler priorities, realtime priority, tick counters, pctcpu, sleep time, original/current CPU, estimated CPU, rusage, signal list/mask, wait channel, wait message, and command name.
- If an LWP is marked runnable but neither LWKT nor user scheduler run-queue flags indicate it is queued, status is adjusted to sleep.
- Kernel threads are reported with pid/tid `-1`, `P_SYSTEM`, idle vs active state, one thread, kernel thread address, priority data, tick counters, CPU id, wait channel/message, and command name.

## Dual Kernel/Userland Compilation

- The file is compiled by both kernel and libkvm.
- In non-kernel builds it defines local `timevalfix()`, `timevaladd()`, and `ruadd()` helpers and declares `devid_from_dev()` externally.
- In kernel builds it uses `get_mplock_count()` for MP lock count; userland reports zero.

## VFS/File-System Relevance

- Exports fd table pointer and controlling tty device id.
- Reports VM sizes and resident counts relevant to file-backed mappings.
- Exports jail id for process visibility and jail-scoped filtering.
- Used by process inspection tools that often correlate open files, cwd/root, tty, and VM state from other kinfo/procfs paths.

## Research Notes

- This file is read-only/export logic and does not mutate process state.
- `fill_kinfo_proc()` explicitly supports zombie/deallocation races through defensive null checks.
- `fill_kinfo_lwp()` doubles as an aggregator, so callers must zero/prepare the target structure as documented.
