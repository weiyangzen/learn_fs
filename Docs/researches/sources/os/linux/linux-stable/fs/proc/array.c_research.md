# File Research: sources/os/linux/linux-stable/fs/proc/array.c

## Purpose

Formats core per-task proc outputs such as `/proc/<pid>/status`, `/proc/<pid>/stat`, `/proc/<pid>/statm`, and optionally `/proc/<pid>/task/<tid>/children`.

## Main Responsibilities

- Task name formatting:
  - `proc_task_name()` chooses worker, kernel thread, or normal task names and optionally escapes output.
- Task status:
  - `task_state()` prints state, pid namespace ids, credentials, groups, FD table size, thread/kernel-thread status.
  - `task_sig()` prints pending, blocked, ignored, caught signals, thread count, and signal queue limits.
  - `task_cap()` prints inheritable, permitted, effective, bounding, and ambient capabilities.
  - `task_seccomp()` prints `NoNewPrivs`, seccomp mode/filter count, and speculation control state.
  - `task_cpus_allowed()`, `task_core_dumping()`, `task_thp_status()`, and `task_untag_mask()` add CPU, coredump, THP, and memory tag data.
  - `proc_pid_status()` composes the full `/proc/<pid>/status`.
- `/proc/<pid>/stat` and `/proc/<pid>/task/<tid>/stat`:
  - `do_task_stat()` gathers pid/session/tty data, faults, CPU times, scheduling fields, RSS/vsize, memory address fields, signal data, wchan flag, delay accounting, guest time, and exit code.
  - `proc_tid_stat()` reports a single thread.
  - `proc_tgid_stat()` reports the whole thread group.
- `/proc/<pid>/statm`:
  - `proc_pid_statm()` prints total, resident, shared, text, lib placeholder, data, and dt placeholder fields.
- Optional `/children`:
  - Under `CONFIG_PROC_CHILDREN`, implements iteration over first-level child pids using `get_children_pid()` and seq operations.

## Key Data/Control Flow

- Uses `get_task_mm()`/`mmput()` when memory data is available.
- Uses `lock_task_sighand()` for signal-related state.
- Uses namespace-aware pid helpers such as `task_pid_nr_ns()`, `task_tgid_nr_ns()`, `task_pgrp_nr_ns()`, and `task_session_nr_ns()`.
- Uses ptrace permission checks to gate sensitive instruction pointer, stack pointer, wchan, and memory address fields.
- Applies time namespace offset to process start boottime in `/stat`.

## Security and Compatibility Notes

- Kernel addresses are not exposed in `/stat`; wchan is reduced to a 0/1 availability flag.
- Some obsolete signal fields remain in `/stat` for Linux 2.0 compatibility.
- `/children` is explicitly documented as not perfectly accurate under concurrent child exit.
