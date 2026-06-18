# sources/distributed-fs/tahoe-lafs/src/allmydata/_monkeypatch.py

## Purpose

This file is the central hook for Tahoe-LAFS third-party monkey patches.

## Important APIs, Types, And Functions

`patch()` is the only function. In the current source it contains only a docstring and performs no patching.

## Control Flow

`allmydata.__init__` imports and calls `patch()` at package import time. Because the function body is empty, control immediately returns.

## State And Persistence

No state is modified in the current implementation.

## Dependencies And Integration Points

It is intentionally integrated into package import. Future compatibility shims for third-party libraries would likely be placed here to run before deeper Tahoe imports.

## Risks

The docstring says "Path third-party libraries", likely meaning "Patch". Adding real monkey patches here would create process-global import-time side effects and would need tight ordering tests. The current empty implementation can mislead readers expecting active compatibility logic.

## Test Signals

Import `allmydata` and verify no third-party objects are changed unexpectedly. If patches are later added, tests should assert idempotence and ordering.
