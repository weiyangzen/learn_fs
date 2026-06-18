# sources/test-tools/stress-ng/core-mincore.h

## Purpose

This header declares page-residency touch helpers.

## Important APIs, Types, And Functions

It exposes `stress_mincore_touch_pages` and `stress_mincore_touch_pages_interruptible`.

## Control Flow

Callers request residency for a buffer, choosing whether the operation should stop when the global continue flag clears.

## State And Persistence Behavior

The implementation may temporarily write to pages but owns no persistent state.

## Dependencies And Integration Points

The API is consumed by mmap and memory stressors controlled by mmap-mincore options.

## Risks And Test Signals

Callers must pass writable memory if fallback touching may occur. Tests should verify buffer contents are restored.
