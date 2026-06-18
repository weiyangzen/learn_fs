# sources/test-tools/stress-ng/stress-signest.c

Purpose: implements the `signest` stressor, recursively raising many different standard and real-time signals from within a signal handler to stress nested signal delivery and alternative signal-stack depth.

Important APIs/types/functions: `stress_signal_t`, `stress_signest_info_t`, `stress_signest_handler`, `stress_signest_ignore`, `stress_signest_shuffle`, `stress_signest_cmp`, `stress_signest`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `sigsetjmp`, `shim_raise`, `stress_signal_handler`, and `stress_signal_name`.

Control flow: the worker builds a deduplicated signal list from compile-time signals plus real-time signals up to `MAX_SIGNALS`, maps an alternative signal stack, installs handlers for all listed signals, synchronizes start, then repeatedly raises the first signal. The handler records stack depth and max nesting depth, increments bogo ops, marks the current signal handled, raises the next signal, and uses longjmp to escape on timeout or stop. Finish disables handlers, logs unique handled signals and stack-depth estimates, records nanoseconds per handled signal, disables altstack, and unmaps it.

State and persistence behavior: state is global signal arrays, counters for raised/handled signals, current signal index, jump buffer, and volatile `signal_info`. There is no persistent storage.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without siglongjmp. It depends on stress-ng stack helpers, signal-name helpers, sorting helpers, and platform signal availability.

Risks and test signals: nested signal recursion can exhaust or bypass alternative stacks, and not all signals are catchable or equally deliverable. Failure is no handled signals after raises, handler install failure, altstack allocation/setup failure, or runaway nested delivery requiring longjmp escape.
