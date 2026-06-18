# sources/test-tools/stress-ng/stress-sigpending.c

Purpose: implements the `sigpending` stressor, verifying blocked SIGUSR1 delivery appears in `sigpending` and disappears after unmasking.

Important APIs/types/functions: `stress_sigpending`, `sigemptyset`, `sigaddset`, `sigprocmask`, `sigpending`, `sigismember`, `shim_kill`, and `stress_signal_ignore_handler`.

Control flow: the worker installs a SIGUSR1 ignore handler, synchronizes start, then each iteration blocks SIGUSR1, sends SIGUSR1 to itself, checks pending membership, unblocks signals, checks SIGUSR1 is no longer pending, exercises invalid and no-op `sigprocmask` calls, and increments bogo ops.

State and persistence behavior: state is the process signal mask and local `sigset_t` values. No external resources persist.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on standard POSIX signal-mask semantics and stress-ng process state helpers.

Risks and test signals: failures indicate incorrect mask setup, signal delivery race, `sigpending` failure, missing pending SIGUSR1, or SIGUSR1 remaining pending after unmask.
