# sources/test-tools/stress-ng/core-limit.h

## Purpose

This header declares the resource-limit maximization entry point.

## Important APIs, Types, And Functions

It exposes `stress_limit_max_set`.

## Control Flow

Callers invoke it during setup before launching stress workloads or child processes.

## State And Persistence Behavior

The implementation mutates current process rlimits. The header owns no state.

## Dependencies And Integration Points

It integrates with option settings for resource-limit overrides.

## Risks And Test Signals

The main API signal is that it is best-effort and returns no status, so tests should inspect resulting limits rather than return codes.
