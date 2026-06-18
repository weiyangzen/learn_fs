# sources/test-tools/ior/src/aiori-DUMMY.c

## Purpose
Provides a synthetic IOR backend that performs no real I/O and optionally sleeps in create, close, sync, and transfer callbacks. It is useful for benchmarking framework overhead, scheduling, and delay behavior.

## Important APIs, Types, and Functions
- `dummy_options_t` stores microsecond delays and whether delays apply only to rank 0.
- `DUMMY_options` allocates backend options and exposes `dummy.delay-create`, `dummy.delay-close`, `dummy.delay-sync`, `dummy.delay-xfer`, and `dummy.delay-only-rank0`.
- `DUMMY_Create` and `DUMMY_Open` return synthetic monotonically increasing pointer values from static `current`.
- `DUMMY_Xfer` returns the requested length after optional delay.
- Metadata functions return success or trivial statfs values; file size is always zero.
- `DUMMY_init` and `DUMMY_final` track `count_init` and warn on lifecycle events.

## Control Flow
The backend requires `DUMMY_init` before create/open and errors if `count_init <= 0`. Delay helper logic is repeated in create, close, sync, and xfer, using `nanosleep` with microsecond option values. Close does not free handles because handles are fabricated pointer values.

## State and Persistence
No persistent state is created. Runtime state is global: synthetic pointer cursor and init count. The backend intentionally does not store file contents or metadata.

## Dependencies and Integration Points
Depends only on standard C/POSIX time functions plus IOR globals and logging. It registers a full mdtest-capable `ior_aiori_t dummy_aiori`.

## Risks and Edge Cases
- Pointer arithmetic on `char *current` fabricates invalid addresses; they must never be dereferenced by generic code.
- Delay conversion assumes microseconds and splits to seconds/nanoseconds.
- Metadata always succeeds, which can mask caller assumptions about real filesystem behavior.
- `DUMMY_Open` has no open delay, unlike create.

## Test Signals
Test lifecycle misuse, rank-0-only delays under MPI, elapsed time for each delay knob, verbose logging, and mdtest behavior with fabricated success responses.
