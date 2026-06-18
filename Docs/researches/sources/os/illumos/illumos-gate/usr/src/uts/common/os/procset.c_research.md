# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/procset.c

## Purpose

`procset.c` implements `procset_t` selection logic for processes and LWPs. It validates procset operands, resolves `P_MYID`, scans process/LWP sets, evaluates set operations, and provides callbacks over matching processes or threads.

Read completely: 941 lines.

## Main Responsibilities

- Validates `procset_t` id types and set operators.
- Iterates over matching processes with `dotoprocs()`.
- Evaluates whether a process belongs to a procset with `procinset()`.
- Evaluates whether an LWP/thread belongs to a procset with `lwpinset()`.
- Detects common procsets that select only the current process/thread.
- Resolves `P_MYID` for all supported id types via `getmyid()`.
- Iterates over matching LWPs in the current process with `dotolwp()`.

## Supported Selection Dimensions

The file supports `P_LWPID`, `P_PID`, `P_PPID`, `P_PGID`, `P_SID`, `P_TASKID`, `P_CID`, `P_UID`, `P_GID`, `P_PROJID`, `P_POOLID`, `P_ZONEID`, `P_CTID`, and `P_ALL`, with operations `POP_DIFF`, `POP_AND`, `POP_OR`, and `POP_XOR`.

## Control Flow And Algorithms

`dotoprocs()` first validates the procset and resolves `P_MYID` operands under `pidlock`. It has a fast path for the common `PID AND ALL` case, avoiding a full process scan. The general path scans `practive`, applies zone access checks, skips embryonic/zombie/system/no-thread processes, calls `procinset()` under each process lock, invokes the callback for matches, and handles the special case where only `init` matched.

`procinset()` evaluates left and right operands against a process under `p_lock`. It handles credentials under `p_crlock`, session IDs under `p_splock`, scheduling class via the representative thread, task/project/pool/zone/contract IDs, and LWP operands only for the current process. It then applies the requested set operation.

`lwpinset()` performs similar operand evaluation for a specific thread, excluding system scheduling class threads. It sets `*done` when both LWP operands identify the same thread, allowing callers to stop early.

`dotolwp()` validates and resolves operands, locks the current process, returns early if the whole process already matches, scans the current process thread list, invokes callbacks for matching threads, and intentionally returns with `p_lock` held in the success path expected by priocntl code.

## Dependencies And Integration

- Used by process-control and scheduling interfaces such as `priocntl`, signal/process operations, and pool binding.
- Integrates with zones, credentials, sessions, tasks, projects, pools, contracts, and scheduler classes.
- `pool.c` relies on `procinset()` for binding target selection.

## Locking And Concurrency

`pidlock` protects global process-list traversal and PID lookup. Individual process fields require `p_lock`, credential checks use `p_crlock`, and session IDs use `p_splock`. The file is careful to skip processes in unstable states (`SIDL`, `SZOMB`, no thread list).

## Notable Risks And Invariants

- Callers must validate procsets before direct `procinset()` / `lwpinset()` use.
- `dotolwp()` has unusual locking semantics: one zero-return path leaves `p_lock` held for historical caller expectations.
- LWP IDs in procsets refer to LWPs in the current process.
- Zone access filtering prevents non-global-zone callers from operating on inaccessible processes.
- Process scans skip system processes except the documented `init` handling.

## Research Relevance

Procsets are a common selection language for process, scheduling, signal, and pool operations. This file is relevant when tracing how a filesystem-related workload or administrative command selects affected processes by project, zone, pool, UID, or task.
