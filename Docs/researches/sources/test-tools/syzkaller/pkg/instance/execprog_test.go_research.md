## sources/test-tools/syzkaller/pkg/instance/execprog_test.go

Purpose: validates VM stream collection behavior and test VM setup helpers without real VM backends.

Important APIs/types/functions: `mockInstance`, `mockPool`, `TestRunStreamAndCollectStdout_*`, `setupTestVM`, and `errorWriter`.

Control flow: mock VM streams stdout/stderr chunks and errors through channels; tests assert success output, write error propagation, context cancellation, command errors, and behavior when error channels are not closed promptly.

State and persistence: mock global pool registration and temp config values only.

Dependencies and integration: depends on `vmimpl` chunk typing and the stream helper contract.

Risks: tests focus on channel semantics, not real SSH/VM multiplex behavior or report parsing.

Test signals: strong coverage for deadlock-prone stream draining and error precedence.
