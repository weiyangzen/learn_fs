# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/proc.c

## Purpose

`proc.c` provides small process-core helpers for process context callback lists and process security flags.

Read completely: 173 lines.

## Main Responsibilities

- Installs and removes process context operation records on a `proc_t`.
- Invokes save, restore, fork, exit, and free callbacks for registered process context operations.
- Frees all registered process context operations during process exit or exec cleanup.
- Checks whether a process security flag is enabled.
- Promotes inherited security flags to effective security flags.

## Important Data Structures

- `struct pctxop`: linked-list node containing callback function pointers (`save_op`, `restore_op`, `fork_op`, `exit_op`, `free_op`), callback argument, and next pointer.
- `p->p_pctx`: per-process head of the context operation list.
- `p->p_secflags`: process security flags with inherited/effective sets.

## Control Flow And Algorithms

`installpctx()` allocates a `pctxop`, fills callbacks and argument, and pushes it onto the process list.

`removepctx()` scans the list with preemption disabled, matches all callback pointers plus the argument, unlinks the node, calls its free callback with `isexec` set to zero if present, frees the node, and reports success.

`savepctx()`, `restorepctx()`, `forkpctx()`, and `exitpctx()` iterate the list and call the corresponding callback when non-NULL. `freepctx()` repeatedly pops and frees all nodes, invoking free callbacks with the supplied exec flag.

`secflag_enabled()` tests one effective flag. `secflags_promote()` copies inherited flags into the effective set.

## Dependencies And Integration

- Process context callbacks are used by subsystems that need per-process state handling during context switch, fork, exec, or exit.
- Security flags are consumed by process execution and policy paths.

## Locking And Concurrency

List mutation in removal/free paths disables kernel preemption to keep traversal stable in this small helper. Save/restore assert current-process context where required.

## Notable Risks And Invariants

- Removal requires exact match of all callback pointers and argument.
- `freepctx()` is the memory cleanup path; `exitpctx()` is for callback actions that must happen before thread memory is freed.
- Callback implementers must tolerate the context and timing implied by save/restore/fork/exit/free entry points.

## Research Relevance

Although small, this file is part of process lifecycle infrastructure used by kernel subsystems that attach state to processes, including mechanisms that can affect filesystem or device behavior across fork/exec/exit.
