# sources/test-tools/stress-ng/stress-sigrt.c

Purpose: implements the `sigrt` stressor, spawning one child per real-time signal and measuring queue-to-wait completion latency across the SIGRTMIN..SIGRTMAX range.

Important APIs/types/functions: `stress_sigrt`, `stress_metrics_t`, `stress_sync_init_pids`, `sigqueue`, `sigwaitinfo`, `sigprocmask`, `stress_kill_and_wait_many`, shared `mmap`, and real-time signal bounds.

Control flow: the worker maps a shared metrics array sized by real-time signal count, allocates PID records, ignores all real-time signals in the parent, synchronizes start, then forks one child per real-time signal. Each child waits for all RT signals and records timing in the shared metrics slot indexed by received signal; it exits on a zero payload and can bounce a SIGRTMIN signal when given a pid payload. The parent loops sending each child its matching signal with a timestamp, increments bogo ops, sends termination notices, and reaps all children.

State and persistence behavior: shared anonymous metrics hold duration/count/t_start per RT signal; child processes hold signal masks. All state is unmapped/freed on exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without sigqueue/sigwaitinfo or RT signal bounds. It depends on stress-ng PID synchronization and kill/reap helpers.

Risks and test signals: systems with large RT ranges can spawn many children; signal queue pressure may return EAGAIN/EINTR. Test signals include successful child reaping, nonzero latency metric count, and absence of unexpected `sigqueue` failures.
