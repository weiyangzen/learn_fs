# sources/test-tools/stress-ng/stress-sighup.c

Purpose: implements the `sighup` stressor, generating SIGHUP through direct raise in a child and through terminal/job-control-like process-group orphan behavior, while measuring handler latency.

Important APIs/types/functions: `stress_sighup_info_t`, `stress_sighup_handler`, `stress_sighup_raise_signal`, `stress_sighup_process_group`, `stress_sighup_closefds`, `stress_sighup`, `fork`, `pipe`, `setpgid`, `kill`, `waitpid`, shared anonymous `mmap`, and SIGHUP handler helpers.

Control flow: the worker installs a SIGHUP handler, maps shared state, synchronizes start, and alternates randomly between two generation modes. Direct mode forks a child that installs the handler and raises SIGHUP. Process-group mode builds a child/grandchild pair with pipes for readiness, moves the grandchild to a process group, stops it, kills the intermediate parent, and waits for kernel SIGHUP delivery before cleanup. Successful iterations increment bogo ops and latency metrics.

State and persistence behavior: process-shared state stores signalled flag, child pid, timestamps, count, and latency. Pipes coordinate readiness and are closed in all local paths.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on fork, process group semantics, SIGSTOP/SIGHUP delivery, and stress-ng kill/wait helpers.

Risks and test signals: process-group SIGHUP behavior is timing-sensitive and OS-dependent. Failures include missing handler invocation, leaked stopped child, pipe coordination failure, wait failure, or latency state not updated.
