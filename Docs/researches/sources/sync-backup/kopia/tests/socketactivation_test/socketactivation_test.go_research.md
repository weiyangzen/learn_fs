<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go -->
# sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go

This file tests Kopia server control socket activation. `TestServerControlSocketActivated` creates a repository and snapshot, opens a TCP listener on an ephemeral port, passes its file descriptor to the server process with `LISTEN_FDS=1`, waits for server stderr parsing to discover the base URL/control password, verifies status over the activated port, and shuts the server down.

`TestServerControlSocketActivatedTooManyFDs` passes two descriptors, expects server startup failure, and asynchronously scans stderr for the expected "too many activated sockets" message to avoid deadlock.

State includes external server process, listener file descriptors, and test CLI config. Dependencies are `KOPIA_SERVER_EXE`, `testenv.CLIExeRunner`, `testutil.ServerParameters`, and network timing. Risks include FD leaks, timing flakes around startup/shutdown, platform-specific activation semantics, and async stderr races. Tests are skipped when the server executable is absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go -->
