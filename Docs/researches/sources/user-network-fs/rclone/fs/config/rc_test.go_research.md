<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc_test.go -->
# sources/user-network-fs/rclone/fs/config/rc_test.go

## Purpose
External-package tests for config RC endpoints.

## Important APIs, Types, And Control Flow
`TestRc` installs a temp config path, creates a local remote through `config/create`, then subtests dump, get, list remotes including env-defined remotes, update, password-obscuring behavior, delete, and empty list shape. Separate tests validate `config/providers`, `config/setpath`, `config/paths`, and both current and legacy unlock password params.

## State And Persistence
The test swaps the global config path and installs configfile storage, restoring the previous path. Environment variable `RCLONE_CONFIG_MY-LOCAL_TYPE` is temporarily set for listremotes.

## Dependencies And Integration Points
Imports the local backend to ensure provider registration. Uses `rc.Calls.Get` and direct handler invocation instead of HTTP.

## Risks And Test Signals
Strong signal for RC JSON contracts and global config mutation. It does not exercise non-interactive continuation state in `rcConfig` beyond basic nil-output behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc_test.go -->
