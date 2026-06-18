# sources/test-tools/stress-ng/core-klog.h

## Purpose

This header declares kernel log monitoring lifecycle functions.

## Important APIs, Types, And Functions

It exposes `stress_klog_start` and `stress_klog_stop(bool *success)`.

## Control Flow

Callers start monitoring before stress execution and stop it afterward, allowing the implementation to update the run success flag.

## State And Persistence Behavior

The implementation owns monitor-child and shared error-count state. The header owns no state.

## Dependencies And Integration Points

The API integrates with global option flags, shared memory, and run success reporting.

## Risks And Test Signals

Callers must pass a valid success pointer on Linux when monitoring is enabled. Tests should cover success flag changes when shared error counts are present.
