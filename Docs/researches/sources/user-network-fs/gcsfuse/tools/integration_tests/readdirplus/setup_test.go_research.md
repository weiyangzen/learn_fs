# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/setup_test.go

## Purpose

`setup_test.go` is the harness for readdirplus integration tests. It prepares config, mounting, storage clients, log parsing helpers, and log validation that differentiates readdirplus from plain readdir and dentry-cache behavior.

## Important APIs, Types, and Functions

Constants define test directory names and GKE temp/log paths. `env` stores storage client, context, test directory, config, and bucket type. `loadLogLines` reads a log stream into lines. `validateLogsForReaddirplus` parses JSON log lines and searches message text for `ReadDirPlus (`, `ReadDir (`, and `LookUpInode (` within a timestamp window. `mountGCSFuseAndSetupTestDir` mounts and creates the test directory. `TestMain` loads config and runs the package.

## Control Flow

`TestMain` parses flags, synthesizes two fallback config items if needed, initializes environment and storage client, handles mounted-directory mode, prepares the test bucket directory, rewrites temp paths, sets static mounting as the only mount mode, runs tests, cleans the test prefix from GCS, and exits with the package result.

## State and Persistence Behavior

The harness stores mutable global `testEnv`, `mountFunc`, `mountDir`, and `rootDir`. It writes trace logs to configured JSON files and creates/deletes `dirForReaddirplusTest` objects in the bucket. Log validation reads the persisted log file after each test action.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, JSON log parsing in `read_logs`, static mounting, setup/test-suite helpers, and `testify/require`. Sibling suites use `validateLogsForReaddirplus` as the behavioral oracle for FUSE operation selection.

## Risks and Edge Cases

`validateLogsForReaddirplus` ignores lines that fail JSON parsing, so non-JSON logs can hide expected signals. Timestamp filtering requires clock consistency and accurate log timestamps. The fallback config only covers static mounting. The `OldGKElogFilePath` compatibility path is a migration accommodation that may become stale.

## Test Signals

Success means both readdirplus suites can create directories, call `ReadDirPlusPicky`, and find expected FUSE operation logs. Harness-level failures usually indicate log path, mount flag, or storage setup problems.
