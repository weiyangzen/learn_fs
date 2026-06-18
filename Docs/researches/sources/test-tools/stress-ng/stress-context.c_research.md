<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-context.c -->
# sources/test-tools/stress-ng/stress-context.c

## Purpose
Implements the `context` stressor, using `getcontext`, `makecontext`, and `swapcontext` to bounce between three user-space contexts and measure context-switch rate.

## Important APIs, Types, and Functions
`stress_context_info` registers the stressor when `ucontext.h` and `swapcontext` are available. `chk_ucontext_t` wraps a `ucontext_t` with canary words. `context_data_t` stores each context, stack mapping, and expected canaries. `stress_context_init()` creates each context and stack. `stress_thread1/2/3()` form a circular swap chain and return to `uctx_main` when stopped.

## Control Flow
`stress_context()` allocates three context records, initializes stacks and canaries, sets `stress_max_ops` from requested bogo max, synchronizes, catches SIGSEGV, starts the chain with `swapcontext(&uctx_main, &context[0])`, then computes bogo operations from `context_counter`. After return, it verifies all canaries, records swapcontext calls per second, unmaps stacks and context data, and returns status.

## State and Persistence Behavior
State is process-local static/global: `uctx_main`, `context`, `context_counter`, and `stress_max_ops`. Stack and context storage are anonymous mmap allocations named for diagnostics. No files or persistent kernel objects are created.

## Dependencies and Integration Points
Depends on ucontext APIs, stress-ng mmap helpers, memory naming, signal handling, random canary generation, process state, metrics, and bogo accounting. It integrates with stress-ng's max-ops limit by scaling context switches to bogo units.

## Risks and Edge Cases
`ucontext` is deprecated or absent on some platforms. Stack size must be sufficient for the context functions. Canary checks detect memory clobbering around `ucontext_t`, but not arbitrary stack corruption. If `swapcontext` fails or a context never returns, cleanup and metrics are affected.

## Test Signals
Good signals are nonzero "swapcontext calls per sec", no canary-clobber failures, correct unimplemented behavior without ucontext support, and stable termination at both time-based and max-ops limits.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-context.c -->
