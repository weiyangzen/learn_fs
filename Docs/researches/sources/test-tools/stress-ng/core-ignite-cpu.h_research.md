# sources/test-tools/stress-ng/core-ignite-cpu.h

## Purpose

This header exposes the CPU ignition lifecycle for starting and stopping maximum-performance CPU setting maintenance.

## Important APIs, Types, And Functions

It declares `stress_ignite_cpu_start` and `stress_ignite_cpu_stop`. All sysfs-specific data structures and state are private to the implementation.

## Control Flow

Callers start ignition before stress work and stop it during teardown. The API is side-effect focused and returns no status, so failures are intentionally best-effort.

## State And Persistence Behavior

The implementation maintains global state and external sysfs side effects. The header itself owns none.

## Dependencies And Integration Points

Consumers need only include the header and link the implementation. The feature integrates with global stress run lifecycle.

## Risks And Test Signals

The main API risk is failing to pair start and stop. Tests should verify repeated start calls are idempotent and stop restores state after partial starts.
