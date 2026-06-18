# sources/test-tools/stress-ng/core-killpid.c

## Purpose

This module provides safe process termination and reaping helpers for stress-ng child processes. It centralizes SIGKILL memory-release optimization on Linux, guards against killing PID 0/1/self, and provides multi-PID kill/wait flows.

## Important APIs, Types, And Functions

Public functions are `stress_kill_pid`, `stress_kill_pid_wait`, `stress_kill_sig`, `stress_wait_until_reaped`, `stress_kill_and_wait`, `stress_kill_many`, `stress_wait_many`, and `stress_kill_and_wait_many`. On Linux with `process_mrelease`, `stress_kill_pid` opens a pidfd, sends SIGKILL, then calls `process_mrelease` to reclaim memory quickly.

## Control Flow

Single-process termination sends the requested signal, then `stress_wait_until_reaped` loops on `waitpid`, handles interrupted waits, checks process existence with `kill(pid, 0)`, escalates when global continue has stopped, optionally accounts forced-killed bogo ops after repeated failures, and emits process diagnostics after a long unkillable interval. Multi-PID helpers send signals to all valid PIDs first, then reap each child to avoid serial kill delays.

## State And Persistence Behavior

The module owns no static state. It changes child process state and can update stressor metrics via `stress_force_killed_bogo`. It may print process diagnostics for stuck children.

## Dependencies And Integration Points

It depends on shim kill/wait/pidfd/process_mrelease wrappers, global continue flag, sleep/yield helpers, logging, process diagnostics, and `stress_pid_t` arrays used by stressor orchestration.

## Risks And Test Signals

Risks include accidentally targeting protected PIDs, indefinite waits for uninterruptible children, and platform-specific pidfd/process_mrelease behavior. Test signals include self/PID1 guard behavior, SIGTERM and SIGKILL paths, wait return status propagation, EINTR handling, multi-child kill-before-wait ordering, and graceful fallback without Linux pidfd support.
