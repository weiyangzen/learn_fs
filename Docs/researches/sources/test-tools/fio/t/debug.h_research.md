# sources/test-tools/fio/t/debug.h

## Purpose
Declares the minimal debug initializer used by test utilities that compile with the local `debug.c` shim.

## Important APIs, Types, and Functions
Exports `debug_init(void)` behind the `FIO_DEBUG_INC_H` include guard.

## Control Flow
No runtime logic exists in the header.

## State and Persistence Behavior
No state is owned by the header; it exposes initialization of the state defined in `debug.c`.

## Dependencies and Integration Points
Included by `dedupe.c` and any similar test binary needing fio logging globals.

## Risks
The header declares only `debug_init()`, so code requiring richer debug APIs still depends on external symbols or the full fio headers.

## Test Signals
Successful compilation of consumers that include `debug.h` verifies the header contract.
