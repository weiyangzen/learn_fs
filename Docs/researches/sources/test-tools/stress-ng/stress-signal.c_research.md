# sources/test-tools/stress-ng/stress-signal.c

Purpose: implements the `signal` stressor, directly exercising the legacy `signal()` API or raw `__NR_signal` syscall by swapping SIGCHLD dispositions and raising SIGCHLD.

Important APIs/types/functions: `stress_signal_count_handler`, `shim_signal`, `stress_signal`, `signal`, optional raw `syscall(__NR_signal)`, `shim_kill`, `SIG_IGN`, `SIG_DFL`, and SIGCHLD.

Control flow: after synchronization, each loop installs SIGCHLD ignore, checks that installation did not spuriously run the counter handler, installs the counter handler, raises SIGCHLD at self, waits for the counter to change, restores default disposition, checks again for spurious delivery, and sets bogo count from the signal counter.

State and persistence behavior: state is a single volatile counter and the process signal disposition for SIGCHLD. No persistent resources are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on syscall availability guards, stress-ng kill/yield wrappers, and standard signal disposition semantics.

Risks and test signals: legacy `signal` semantics vary between BSD/POSIX behavior. Failures include inability to install handlers, counter changes during disposition changes, failure to receive raised SIGCHLD, or incorrect restoration to default.
