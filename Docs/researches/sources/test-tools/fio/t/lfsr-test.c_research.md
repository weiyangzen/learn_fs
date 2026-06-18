# sources/test-tools/fio/t/lfsr-test.c

## Purpose
Interactive benchmark and verifier for fio's linear-feedback shift register sequence generator.

## Important APIs, Types, and Functions
Uses `struct fio_lfsr`, `lfsr_init()`, and `lfsr_next()`. `main()` accepts the number of values in hex, optional seed, spin count, and a `verify` flag, then prints LFSR parameters and timing.

## Control Flow
After argument parsing and architecture initialization, the program initializes the LFSR. In verify mode it allocates one byte per expected number and marks each generated value. It loops until `lfsr_next()` reports completion, optionally validates every value appeared exactly once, computes elapsed microseconds, and returns zero or verification failure.

## State and Persistence Behavior
No persistent state. Verification can allocate large memory proportional to the requested sequence length. Output is split between stdout summaries and stderr progress.

## Dependencies and Integration Points
Depends on fio LFSR, timing, architecture, and compiler fallthrough helpers. It validates random-offset generation infrastructure used by fio.

## Risks
Verification memory is unbounded relative to user input. Pointer arithmetic on `void *` is a compiler extension. `atol()`/`atoi()` parsing is permissive and seed is decimal while count is hex.

## Test Signals
Signals include successful initialization for valid sizes, full-cycle uniqueness in verify mode, and stable mean generation timing for performance comparison.
