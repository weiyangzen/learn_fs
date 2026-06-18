<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c

Purpose: verifies a signal pending in the parent is not pending in a `vfork()` child.

Important APIs/types/functions: `setup()` installs a `SIGUSR1` handler, blocks `SIGUSR1`, sends it to the parent, and verifies it is pending. `run()` uses `vfork()` and the child checks `sigpending()` plus `sigismember(SIGUSR1) == 0`. `cleanup()` unblocks the signal.

Control flow/state: parent accumulates a blocked pending signal before the test. The child inspects its own pending set and exits without disturbing parent cleanup.

Dependencies/integration: standard POSIX signal APIs via LTP safe wrappers; `.forks_child = 1` ensures child reaping.

Risks/test signals: signal-mask inheritance and pending-signal semantics are subtle; this specifically asserts pending signals are per-process and not inherited. Failures are either setup inability to create the pending signal or child observation of inherited pending state.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork02.c -->
