# sources/test-tools/stress-ng/stress-sigtrap.c

Purpose: implements the `sigtrap` stressor, raising SIGTRAP either via `raise` or, on Linux x86, an `int $3` trap instruction, then measuring handler latency.

Important APIs/types/functions: `stress_sigtrap_handler`, `stress_sigtrap`, `shim_raise`, x86 inline `int $3`, `stress_signal_handler`, volatile counter/timestamp/duration state, and metrics export.

Control flow: the worker installs the SIGTRAP handler, synchronizes start, then loops randomly choosing an architecture trap path or `raise(SIGTRAP)`. The handler records elapsed time from the pre-raise timestamp and increments a counter; the worker mirrors that counter into bogo ops and validates that at least one raised trap was handled.

State and persistence behavior: all state is volatile process-local counters and timing variables. No external resources are allocated.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. If SIGTRAP is not defined, the stressor reports unimplemented through a supported callback.

Risks and test signals: trap-instruction availability is platform-specific. Failures include no handled traps despite raises, handler installation failure, and nonsensical latency metrics.
