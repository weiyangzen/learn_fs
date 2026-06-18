# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pgrp.c

## Purpose

`pgrp.c` implements process group membership, process-group signaling, and orphaned process group detection for job control.

Read completely: 258 lines.

## Main Responsibilities

- Adds and removes processes from process group lists.
- Sends signals to all members of a process group.
- Tracks whether a process group is orphaned.
- Detects when exiting parents orphan child process groups.
- Sends SIGHUP and SIGCONT to stopped orphaned groups as required by job-control semantics.
- Tests whether a process group has members other than its leader.

## Process Group Lists

Each process group is represented by a `struct pid` whose `pid_pglink` points to the head process and `pid_pgtail` to the tail. Each process uses `p_pglink` and `p_ppglink` for next and previous links, plus `p_pgidp` for the group ID object.

All structural operations assert or acquire `pidlock`.

## Membership and Orphan Tracking

`pglinked()` returns true when a process has a parent in the same session but outside the process group. Such a parent prevents the group from being orphaned.

`pgjoin()` inserts linked processes at the head and unlinked processes at the tail. On first membership it holds the process-group PID object with `PID_HOLD()` and initializes `pid_pgorphaned`. If an orphaned group gains a linked process, it clears the orphaned flag.

`pgexit()` unlinks a process from its group, releases the PID object when the group becomes empty, and recomputes orphaned state if a formerly non-orphaned group may have lost its last external parent link.

`pgdetach()` handles a parent process exiting. It walks children, checks whether each child's group becomes orphaned, and if the group is stopped sends SIGHUP followed by SIGCONT.

## Signaling Helpers

`pgsignal()` acquires `pidlock` and calls `sigtoproc()` for every group member under each process lock.

`sigtopg()` performs the same loop but requires the caller to already hold `pidlock`.

`pgmembers()` returns true if a process group contains a process whose PID differs from the group ID, meaning the group has members beyond its leader.

## Notable Invariants

- `pidlock` protects process group list structure.
- Process locks are acquired while walking group membership to deliver signals.
- Nonempty process groups hold their `struct pid`; empty groups release it.
- Orphan transitions can produce SIGHUP/SIGCONT only when stopped members are present.

## Research Relevance

This file is general process-control infrastructure. It is relevant to filesystem research primarily through signal and session semantics that affect shell-driven jobs, daemons, and processes blocked in filesystem operations.
