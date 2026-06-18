# sources/test-tools/stress-ng/core-io-priority.c

## Purpose

This module parses ionice class names and applies Linux I/O priority settings through the `ioprio_set` syscall when available.

## Important APIs, Types, And Functions

`stress_io_priority_ionice_class_get` maps strings such as `idle`, `besteffort`, `be`, `realtime`, and `rt` to `IOPRIO_CLASS_*` constants. `stress_io_priority_set` validates class and level, normalizes defaults, and calls `shim_ioprio_set(IOPRIO_WHO_PROCESS, 0, IOPRIO_PRIO_VALUE(...))` on systems with `__NR_ioprio_set`; otherwise it is a no-op.

## Control Flow

Class parsing exits the process on invalid input after printing available options. Priority setting returns success for `UNDEFINED`, clamps idle to level zero with an informational message, rejects invalid realtime/besteffort levels outside 0-7, and reports syscall failures except `ENOSYS`.

## State And Persistence Behavior

The module changes the current process I/O priority. It owns no persistent internal state. Unsupported systems leave priority unchanged.

## Dependencies And Integration Points

It depends on constants declared in `core-io-priority.h`, logging functions, shim syscall wrappers, and command-line option parsing that supplies class and level values.

## Risks And Test Signals

Risks include terminating on parse errors, permission failures for realtime priority, and unsupported kernels. Test signals include correct mapping aliases, invalid class diagnostics, level validation, no-op behavior without syscall support, and preservation of success when syscall returns `ENOSYS`.
