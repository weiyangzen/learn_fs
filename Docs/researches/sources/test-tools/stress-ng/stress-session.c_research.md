# sources/test-tools/stress-ng/stress-session.c

Purpose: implements the `session` stressor, repeatedly creating child and grandchild processes that call `setsid`, validate `getsid`, exercise `vhangup`, and mix waited and orphaned process paths.

Important APIs/types/functions: `session_error_t`, `stress_session_error`, `stress_session_return_status`, `stress_session_set_and_get`, `stress_session_child`, `stress_session`, `setsid`, `getsid`, `fork`, `waitpid`, optional `wait4`, `pipe`, and `shim_vhangup`.

Control flow: the parent creates a pipe and synchronizes start. For each iteration it forks a child; the child closes the read end, creates a new session, forks a grandchild, and either waits for the grandchild or intentionally leaves it orphaned about 25 percent of the time. The grandchild also creates a session, calls `vhangup`, writes a success status, and exits. The parent reads a structured error from the pipe, waits for the child, reports failures, and increments bogo ops.

State and persistence behavior: state is transient process/session state plus a pipe-carried status structure. No filesystem persistence is created. Resource failures for grandchild fork are treated as successful no-resource pressure in the child path.

Dependencies and integration points: registered as `CLASS_SCHEDULER | CLASS_OS` with always verify. It depends on process creation, wait semantics, stress-ng process state reporting, and optional rusage collection through `wait4`.

Risks and test signals: risks include fork pressure, races around orphan reaping, pipe read ordering, and platform-specific `vhangup` behavior. Test signals are failures from `setsid`, `getsid`, mismatched session ids, fork/wait failures, or unexpected child exit statuses.
