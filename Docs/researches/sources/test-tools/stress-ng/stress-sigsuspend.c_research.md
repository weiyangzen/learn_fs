# sources/test-tools/stress-ng/stress-sigsuspend.c

Purpose: implements the `sigsuspend` stressor, waking child processes blocked in `sigsuspend` by repeatedly sending SIGUSR1 from the parent.

Important APIs/types/functions: `stress_sigsuspend`, `sigsuspend`, `sigprocmask`, `stress_signal_ignore_handler`, `stress_signal_stop_flag_handler`, `stress_lock_create`, `stress_bogo_inc_lock`, `fork`, `kill`, `waitpid`, and `stress_kill_pid_wait`.

Control flow: the worker installs SIGUSR1 ignore and SIGCHLD stop handlers, creates a shared counter lock, captures the old signal mask, synchronizes start, and forks up to four children. Each child loops in `sigsuspend(&mask)` and exits on unexpected errors or when locked bogo increment says stop. The parent loops over children, sending SIGUSR1 while updating the locked bogo counter, then reaps or kills children and destroys the lock.

State and persistence behavior: state is transient child PIDs, process signal masks, and a stress-ng lock named `counter`. No durable storage is created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on stress-ng locking, kill/wait helpers, CPU affinity, and scheduler settings for children.

Risks and test signals: races around child exit versus signal send are expected. Failures include unexpected `sigsuspend` errors in children, fork failure, lock creation failure, premature child death, or bogo counter inconsistencies.
