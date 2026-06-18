# sources/test-tools/stress-ng/stress-sigvtalrm.c

Purpose: implements the `sigvtalrm` stressor, arming `ITIMER_VIRTUAL` with a 1 microsecond interval so CPU consumption generates SIGVTALRM signals.

Important APIs/types/functions: `stress_sigvtalrm_set`, `stress_sigvtalrm_handler`, `stress_sigvtalrm`, `setitimer`, `getitimer`, `ITIMER_VIRTUAL`, `SIGVTALRM`, `getrusage`, and bogo counter helpers.

Control flow: the worker installs a SIGVTALRM handler, synchronizes start, arms a virtual interval timer, then loops calling `getitimer` while CPU time advances. The handler increments bogo ops and cancels the timer when the run should stop. At exit the worker optionally verifies that a run with more than one second of user CPU handled at least one SIGVTALRM, then cancels the timer.

State and persistence behavior: state is a process virtual timer and global args pointer. The timer is explicitly zeroed during handler stop and deinit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without `getitimer`, `setitimer`, `ITIMER_VIRTUAL`, or SIGVTALRM support.

Risks and test signals: timer granularity and implementation differ by OS. Failures include `setitimer` not implemented, no handled signals after sufficient CPU time, or a timer left running after stop.
