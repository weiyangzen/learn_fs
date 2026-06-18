<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-cmd.c -->
## sources/test-tools/strace/tests/attach-p-cmd-cmd.c

Purpose: Command-side tracee for `attach-p-cmd` tests, publishing its pid and waiting for peer coordination before producing output.

Important APIs/types/functions: Defines `write_pidfile`, `wait_for_peer_invocation`, uses `fopen/fprintf/fclose`, `rmdir`, `chdir`, `sprintrc`, and constants from `attach-p-cmd.h`.

Control flow: Writes its pid to `attach-p-cmd.test-pid`, waits until the peer-created lock directory can be removed, attempts the expected `chdir`, prints pid-prefixed syscall and exit lines.

State and persistence: Creates a pid file and removes the lock directory created by the peer; pid file is later removed by the peer.

Dependencies and integration: Coordinates with `attach-p-cmd-p.c` via `lockdir` and `pidfile`. Used by the attach-p command test script.

Risks: Busy waiting on filesystem state can fail if stale lock/pid files exist or if cleanup from prior failures is incomplete.

Test signals: Expected command pid appears in pid file and output contains failed `chdir("attach-p-cmd.test cmd")`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-cmd.c -->
