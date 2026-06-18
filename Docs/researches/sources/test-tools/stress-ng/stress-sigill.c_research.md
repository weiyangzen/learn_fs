# sources/test-tools/stress-ng/stress-sigill.c

Purpose: implements the `sigill` stressor, executing architecture-specific illegal instructions, recovering via `siglongjmp`, and optionally verifying SIGILL siginfo codes.

Important APIs/types/functions: architecture-specific `stress_illegal_op`, `stress_sigill_handler`, `stress_sigill`, `sigaction`, `sigsetjmp`, `SIGILL`, optional SIGBUS handler registration, `ILL_*` code checks, and `stress_signal_siglongjmp`.

Control flow: compile-time architecture guards define one illegal instruction emitter. The worker synchronizes start, repeatedly establishes a jump point, verifies the prior signal on the return path, increments bogo ops, installs SIGILL and SIGBUS handlers, and calls the illegal-op function to trigger the next signal.

State and persistence behavior: global signal state records the last fault address, signum, code, and jump buffer. There is no persistent filesystem or IPC state.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify with `SA_SIGINFO`, and unimplemented unless the architecture has an illegal-op function plus SIGILL and siglongjmp support.

Risks and test signals: illegal instruction encodings vary by architecture and may produce SIGBUS or nonstandard codes. Test signals are repeated recovery, recognized `ILL_*` codes in verify mode, and correct unimplemented reporting when support is absent.
