# sources/test-tools/stress-ng/core-mlock.h

## Purpose

This header declares the memory-locking region helper.

## Important APIs, Types, And Functions

It exposes `stress_mlock_region(const void *addr_start, const void *addr_end)`.

## Control Flow

Callers pass a half-open address range and receive the `mlock` result or success for empty/unsupported cases.

## State And Persistence Behavior

The implementation can change process memory residency/lock state. The header owns no state.

## Dependencies And Integration Points

It integrates with signal and memory subsystems that need pages locked in RAM.

## Risks And Test Signals

Callers should handle nonzero returns caused by limits or permissions. Alignment tests are the key signal.
