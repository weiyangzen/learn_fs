# sources/test-tools/stress-ng/core-try-open.h

## Purpose
`core-try-open.h` defines status codes and prototypes for bounded-risk open probes.

## Important APIs, Types, And Functions
Status codes are `STRESS_TRY_OPEN_OK`, `STRESS_TRY_OPEN_FORK_FAIL`, `STRESS_TRY_OPEN_WAIT_FAIL`, `STRESS_TRY_OPEN_EXIT_FAIL`, `STRESS_TRY_OPEN_FAIL`, and `STRESS_TRY_AGAIN`. The exported functions are `stress_try_open` and `stress_try_open_timeout`.

## Control Flow
Callers invoke one of the probe helpers with a path, flags, and nanosecond timeout. Results distinguish success, retryable device-busy/resource cases, child-management failures, and open failure.

## State And Persistence
No state is declared in the header. Implementation state is transient child/timer state.

## Dependencies And Integration Points
It depends on `stress_args_t` and common integer/time types from `stress-ng.h`. Stressors that handle special files, drivers, or devices integrate with these return codes to skip or retry safely.

## Risks
Callers must handle both the documented status constants and `-1` from the implementation's pre-stat failure. Misinterpreting `STRESS_TRY_AGAIN` as hard failure can reduce coverage on temporarily busy devices.

## Test Signals
Build coverage validates prototypes. Runtime signals appear in device/file stressors that skip problematic paths instead of hanging.
