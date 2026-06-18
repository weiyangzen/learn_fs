<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config_test.go -->
# sources/user-network-fs/rclone/cmd/config/config_test.go

## Purpose

`config_test.go` unit-tests the key/value parser used by config create, update, and password commands.

## Important APIs, Types, and Functions

`TestArgsToMap` exercises `argsToMap` with empty input, alternating `key value`, `key=value`, mixed forms, and dangling keys.

## Control Flow

The table-driven test converts each argument slice and asserts either an exact `rc.Params` map or an error.

## State and Persistence Behavior

No config file is touched. The test is pure parser validation.

## Dependencies and Integration Points

It depends on `fs/rc.Params`, `testify/assert`, and the unexported parser in the same package.

## Risks and Test Signals

The test signals parsing correctness but does not cover duplicate keys, empty key/value strings, shell quoting, or command-level side effects. Additional tests should cover those boundaries and non-interactive config flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config_test.go -->
