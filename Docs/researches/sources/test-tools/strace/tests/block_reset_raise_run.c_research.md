<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_raise_run.c -->
## sources/test-tools/strace/tests/block_reset_raise_run.c

Purpose: Helper launcher that blocks a signal, resets its handler to default, raises it pending, then execs another command.

Important APIs/types/functions: Uses `sigemptyset`, `sigaddset`, `sigprocmask(SIG_BLOCK)`, `signal(SIG_DFL)`, `raise`, and `execvp`.

Control flow: Parses `signo` and command arguments, blocks the signal, installs default handling, raises the signal while blocked, then execs the requested program.

State and persistence: Signal mask and pending signal are inherited across `execvp`; no filesystem state.

Dependencies and integration: Used by signal/status tests that need a target process with a blocked pending default signal at exec time.

Risks: Invalid signal numbers or exec failures abort with harness error. Signal inheritance semantics are central to expected behavior.

Test signals: The child command should start with the chosen signal blocked and pending, allowing tracer status/term-signal tests to observe it.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_raise_run.c -->
