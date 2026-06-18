<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh -->
# sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh

This tiny shell wrapper prepares environment for socket activation tests. It forwards to the Kopia server executable while setting activation-related variables such as `LISTEN_PID` as expected by systemd-style socket activation.

Control flow is a direct exec-style wrapper around server startup. Its integration point is `socketactivation_test.go`, which passes listener file descriptors through `CLIExeRunner.ExtraFiles` and relies on the wrapper to make those descriptors visible to the server process.

Risks are shell portability, argument forwarding, and environment correctness. Test signals are the socket activation integration tests that require `KOPIA_SERVER_EXE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh -->
