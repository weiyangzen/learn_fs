# sources/test-tools/stress-ng/stress-fma.c

Purpose: implements `fma`, a floating-point compute stressor that repeatedly applies multiply-add and multiply-subtract patterns to aligned float and double arrays, optionally using libc `fma()`/`fmaf()` shims.

Important APIs/types/functions: `stress_fma_t` stores aligned initial, working, and verification arrays for 512 doubles and floats plus scalar operands. `stress_fma_funcs[]` contains hand-written add/sub variants for 132, 213, and 231 operand orderings in double and float forms. When available, `stress_fma_libc_funcs[]` mirrors those operations through `shim_fma()` and `shim_fmaf()`. `stress_fma_init()` fills random initial values; `stress_fma_reset_a()` restores both working copies.

Control flow: `stress_fma()` selects libc or non-libc function arrays, catches SIGILL, mmaps the state object, initializes data after sync, and loops. Each iteration resets arrays, advances operand indices, runs six functions from either the add or subtract half of the table, increments bogo, optionally repeats the same computations on the second copy and byte-compares float/double results, then flips the offset between the two halves.

State and persistence behavior: state is one anonymous private mapping named `fma-data`, marked mergeable. No durable state is created. Floating-point data mutates every iteration but is reset from the initial arrays before each operation set.

Dependencies and integration points: uses math headers, stress-ng target clones, pragma unroll helpers, mmap/madvise, put/shim utilities, and SIGILL handling for CPU feature safety. Registered as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE`, with optional verification and `--fma-libc`.

Risks: exact byte comparison under `--verify` assumes deterministic results between identical runs in the same process and function path, not equivalence between libc and non-libc paths. Target-cloned code and fused operations may trigger SIGILL on misdetected CPU support, hence the signal guard. The optional `USE_FMA_FAST` macro is disabled, so `FP_FAST_FMA*` names are not used unless that macro changes.

Test signals: run default and `--fma-libc` builds with and without `--verify`, across CPUs with and without hardware FMA. Confirm SIGILL is caught rather than crashing, verification arrays remain identical, and fallback messaging appears when libc fma helpers are unavailable.
