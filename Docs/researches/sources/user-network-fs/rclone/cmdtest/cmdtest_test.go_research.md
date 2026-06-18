<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest_test.go -->
# sources/user-network-fs/rclone/cmdtest/cmdtest_test.go

## Purpose

`cmdtest_test.go` supplies the process-reexecution harness used by rclone CLI integration tests.

## Important APIs, Types, and Functions

`TestMain` switches between parent test mode and child CLI mode using `RCLONE_TEST_MAIN`. Helpers include `rcloneExecMain`, `rcloneEnv`, `rclone`, `getEnvInitial`, `createTestEnvironment`, `createTestFile`, `createTestFolder`, and `createSimpleTestData`.

## Control Flow

Parent tests set `RCLONE_TEST_MAIN=true` and run normal tests. Child invocations are spawned with `exec.Command(os.Args[0], args...)`, a cleaned environment without unrelated `RCLONE_` variables, optional semicolon-delimited overrides, and a test config path. The demonstration test checks version output, debug flags, unknown flag errors, env-driven logging, config creation, and local listing.

## State and Persistence Behavior

State is isolated under `t.TempDir`, with `testFolder` and `testConfig` globals set per test. Child process state is isolated by environment construction.

## Dependencies and Integration Points

It tests the real Cobra/root command path, environment parsing, local backend config, and command output/error behavior.

## Risks and Test Signals

Risks include semicolon env parsing limitations, global `envInitial` reuse across changed parent env, and platform differences in child process execution. Signals include successful real command execution, debug logging behavior, error exit status, and config-backed local listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest_test.go -->
