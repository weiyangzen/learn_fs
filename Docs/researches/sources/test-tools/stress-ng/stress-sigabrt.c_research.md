# sources/test-tools/stress-ng/stress-sigabrt.c

Purpose: implements the `sigabrt` stressor, repeatedly generating child process aborts with and without an installed SIGABRT handler and validating that the expected handler path occurs.

Important APIs/types/functions: `stress_sigabrt_info_t`, `stress_sigabrt_handler`, `stress_sigabrt`, `stress_signal_handler`, `abort`, `shim_raise`, `fork`, `waitpid`, shared anonymous `mmap`, and SIGABRT status inspection.

Control flow: the worker installs a handler, maps shared signal state, synchronizes start, then forks one child per iteration. The child either installs the handler and calls `abort`, or restores the default handler and raises SIGABRT. The parent waits, verifies the child died from SIGABRT, verifies handler state according to the chosen mode, increments bogo ops, and records handler latency.

State and persistence behavior: shared MAP_SHARED state records whether the handler was enabled, whether it ran, start time, count, and latency. It is unmapped on exit and has no persistence beyond the worker.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on signal helper installation, fork/wait handling, stress-ng random selection, and process-shared anonymous memory.

Risks and test signals: failures are child not aborting, wrong signal status, handler not called when expected, handler called when default death was expected, fork pressure, or zero/invalid latency accounting.
