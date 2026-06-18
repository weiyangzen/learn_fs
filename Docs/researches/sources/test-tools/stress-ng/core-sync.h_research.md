# sources/test-tools/stress-ng/core-sync.h

## Purpose
`core-sync.h` exposes the process-start synchronization API and inline state accessors used by stressors that coordinate forked workers.

## Important APIs, Types, And Functions
The header defines the state constants `STRESS_SYNC_START_FLAG_WAITING`, `STARTED`, `RUNNING`, and `FINISHED`. It declares shared PID array allocation, start wait/continue helpers, PID initialization, PID tree insertion, and PID lookup. Inline helpers `stress_sync_state_store` and `stress_sync_state_load` use sequentially consistent compiler atomics when available, and `stress_sync_start_s_pid_list_add` pushes a record onto a linked list.

## Control Flow
Callers initialize `stress_pid_t` records, add active records to a list, let children wait through `stress_sync_start_wait*`, and let parents continue the list when all children reach the waiting state. State transitions flow waiting to running to finished, with started used during initialization.

## State And Persistence
The only state touched by the header is the caller-owned `stress_pid_t` memory, commonly shared anonymous mmap memory. No filesystem persistence exists.

## Dependencies And Integration Points
It depends on `stress_pid_t`, `stress_args_t`, attribute macros, atomic builtins, and global sync-start flags from `stress-ng.h`. It is included by `core-sync.c` and stressors that fork children directly.

## Risks
Consumers must keep the linked list and tree links distinct and must not reuse a `stress_pid_t` without reinitialization. The non-atomic fallback can require polling loops and may be weak on unusual memory models. State constants are part of the parent/child protocol, so changes must be coordinated with `core-sync.c`.

## Test Signals
Build coverage validates atomic feature guards. Runtime signals come from `--sync-start` in multi-process stressors; stuck waiting, premature start, or missing child continuation indicates header/API misuse.
