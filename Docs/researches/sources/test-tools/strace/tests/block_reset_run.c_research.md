<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_run.c -->
## sources/test-tools/strace/tests/block_reset_run.c

Purpose: Helper launcher that blocks a signal, resets its handler to default, and execs another command.

Important APIs/types/functions: Uses `sigemptyset`, `sigaddset`, `sigprocmask(SIG_BLOCK)`, `signal(SIG_DFL)`, and `execvp`.

Control flow: Validates arguments, blocks the requested signal, sets default disposition, then replaces the process image with the target command.

State and persistence: The signal mask is inherited by the executed program; no persistent external state.

Dependencies and integration: Used by signal handling tests that need controlled blocked/default signal state without a pending raised signal.

Risks: Invalid signal names/numbers and exec failure produce fatal harness output. Behavior depends on POSIX signal inheritance across exec.

Test signals: Executed program should run under the requested blocked signal with default disposition.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/block_reset_run.c -->
