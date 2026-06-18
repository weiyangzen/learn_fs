# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/icache.c

## Scope

Instruction-cache hook stubs for `5i`.

## Behavior

- `icacheinit()` is empty.
- `updateicache()` accepts an address and marks it used, but performs no cache accounting.

## Dependencies

Uses `arm.h`.

## Risks And Invariants

- `ifetch()` calls `updateicache()` when `icache.on`, but this file provides no implementation, so instruction cache statistics are unavailable.
