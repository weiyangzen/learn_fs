# sources/sync-backup/kopia/cli/command_benchmark_test.go

## Purpose
Test coverage for `command_benchmark` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.

## APIs, Types, and Functions
Important APIs include functions/methods `TestCommandBenchmarkCrypto`, `TestCommandBenchmarkEncryption`, `TestCommandBenchmarkHashing`, `TestCommandBenchmarkSplitter`, `TestCommandBenchmarkCompression`; tests TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, os, path/filepath, testing, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages bytes, os, path/filepath, testing.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. test signals come from named tests TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.
