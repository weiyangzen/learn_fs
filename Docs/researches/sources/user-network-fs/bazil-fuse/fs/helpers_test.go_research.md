<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/helpers_test.go -->
# sources/user-network-fs/bazil-fuse/fs/helpers_test.go

Purpose: top-level fs package test `TestMain` for spawntest helpers.

Important APIs, types, and functions: adds helper flags to `flag.CommandLine`, parses flags, dispatches helper mode with `helpers.RunIfNeeded`, and exits with `m.Run`.

Control flow: helper subprocesses do not run the normal test suite; normal processes continue to tests.

State and persistence behavior: process-wide flags and helper registry only.

Dependencies and integration points: supports fs package tests that register helpers such as lock helpers.

Risks and test signals: missing this setup would make helper subprocess tests fail on unknown flags or no HTTP server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/helpers_test.go -->
