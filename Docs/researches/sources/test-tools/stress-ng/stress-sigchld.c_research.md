# sources/test-tools/stress-ng/stress-sigchld.c

Purpose: implements the `sigchld` stressor, generating and classifying SIGCHLD notifications from children that exit, stop, continue, or are killed.

Important APIs/types/functions: `stress_sigchld_handler`, `stress_sigchld`, `sigaction`, `SA_SIGINFO`, `CLD_EXITED`, `CLD_KILLED`, `CLD_STOPPED`, `CLD_CONTINUED`, `fork`, `kill`, `stress_kill_pid_wait`, and metrics counters.

Control flow: the worker installs a SIGCHLD siginfo handler, synchronizes start, then repeatedly forks a child that exits immediately. The parent sends SIGSTOP and SIGCONT when possible and then kills/waits for the child. The handler increments per-`si_code` counters and the worker sets bogo count from total SIGCHLD deliveries.

State and persistence behavior: all state is process-local volatile counters reset at worker start. Metrics export child-exited/killed/stopped/continued totals.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on signal siginfo semantics, fork/wait/kill helpers, and excludes strict `si_code` verification on OpenBSD.

Risks and test signals: signal coalescing and platform `si_code` behavior can reduce or alter counts. Failure is reported when SIGCHLDs are handled but none have recognized codes on conforming platforms, or when fork/handler installation fails.
