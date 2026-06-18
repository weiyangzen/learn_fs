# sources/user-network-fs/rclone/fs/logger/logger_test.go

## Purpose
`logger_test.go` drives CLI-level logger tests through the `testscript` framework, excluding Plan 9 via build tag.

## Important APIs, types, and functions
`TestMain` registers a synthetic `rclone` command backed by `logger.Main`. `TestLogger` calls `testscript.Run` with `Dir: "testdata/script"` and a setup hook that defines `SRC` and `DST` environment variables under `$WORK`.

## Control flow
The testscript framework runs each script file in the script directory. Scripts can call `rclone`, create files, compare outputs, and use the `SRC`/`DST` directories prepared by setup.

## State and persistence behavior
All filesystem state should live under testscript's `$WORK` temporary directory. Environment variables are set per script environment. No repository files are modified by normal runs.

## Dependencies and integration points
The test depends on `logger.Main`, `testscript`, and rclone's full CLI registry. It is an end-to-end integration point for logging behavior that is difficult to validate with unit tests alone.

## Risks and edge cases
Script outcomes depend on script contents not shown in this subset. Because it imports and runs the real CLI, failures can arise from unrelated backend/command initialization. Plan 9 is excluded, likely due to script or filesystem semantics.

## Test signals
The file signals the presence of black-box CLI regression tests for sync/bisync logger behavior, with source/destination paths isolated in temporary directories.

Source-read signal: reviewed complete local file (34 lines). Functions/methods observed: `TestMain`, `TestLogger`.
