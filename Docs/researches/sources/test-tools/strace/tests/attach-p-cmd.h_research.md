<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd.h -->
## sources/test-tools/strace/tests/attach-p-cmd.h

Purpose: Shared constants for the `attach-p-cmd` companion programs.

Important APIs/types/functions: Defines `static const char lockdir[] = "attach-p-cmd.test-lock"` and `pidfile[] = "attach-p-cmd.test-pid"`.

Control flow: Header-only; no runtime flow.

State and persistence: Names the lock directory and pid file that companion programs create/remove.

Dependencies and integration: Included by both `attach-p-cmd-cmd.c` and `attach-p-cmd-p.c`.

Risks: Changing names without matching shell harness cleanup would break coordination.

Test signals: Both companion binaries must agree on the same lock and pid file names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd.h -->
