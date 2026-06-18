# sources/test-tools/stress-ng/core-killpid.h

## Purpose

This header declares process kill and wait helpers used by stress-ng lifecycle management.

## Important APIs, Types, And Functions

It exposes single-PID helpers, wait-until-reaped, kill-and-wait, and array-based kill/wait helpers. It references `stress_args_t` and `stress_pid_t` project types.

## Control Flow

Callers can use the combined helpers for normal teardown or separate kill and wait phases for bulk child cleanup.

## State And Persistence Behavior

The implementation mutates process state but owns no persistent internal state.

## Dependencies And Integration Points

The API integrates with stressor child process tracking, failure accounting, and cleanup paths.

## Risks And Test Signals

The most important contract is guarding invalid/sensitive PIDs while still reliably reaping children. Tests should exercise both individual and many-PID functions.
