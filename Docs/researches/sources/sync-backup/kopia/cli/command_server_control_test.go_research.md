<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_control_test.go -->
# sources/sync-backup/kopia/cli/command_server_control_test.go

Purpose: end-to-end tests for server control commands over HTTP and Unix domain sockets.

Important APIs/types/functions: `TestServerControl`, `TestServerControlUDS`, `hasLine`, `testutil.ServerParameters`, `RunAndProcessStderr`, server status/refresh/flush/snapshot/cancel/pause/resume/throttle/shutdown commands, and `throttling.Limits`.

Control flow: the main test creates snapshots under two repository identities, starts an insecure server on a random port, waits for managed sources to appear, checks remote source display, refreshes after an external snapshot, flushes, triggers snapshots for all and one source, checks invalid source/no-source failures, cancels, pauses/resumes, sets/gets throttle limits including JSON, shuts down, and verifies later control calls fail. The UDS test starts the server on `unix:<path>` and verifies status/shutdown.

State/persistence behavior: creates repository snapshots, starts/stops a server, mutates server throttling, and sends source-manager control actions.

Dependencies/integration: broad coverage of server API client flags, authentication, source manager, throttle endpoints, shutdown, and platform-specific Unix sockets. Risks/test signals: timing-sensitive waits use `Eventually` and startup/shutdown timeouts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_control_test.go -->
