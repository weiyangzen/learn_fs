# sources/user-network-fs/blobfuse2/azure-pipeline-templates/invalid-command-tests.yml

## Purpose
This template checks that Blobfuse2 commands return the expected invalid-flag exit code when passed unsupported options.

## Important APIs, Types, and Functions
It invokes root `blobfuse2`, `mount`, `unmount`, `mountv1`, `secure`, and `version` commands with `--invalid-param` and expects exit code `2`.

## Control Flow
Each script starts the command in the background and immediately checks `$?`, exiting success only when the command launch returned `2`.

## State and Persistence Behavior
No persistent state is intended. Some commands reference `$(MOUNT_DIR)` but should fail before mutating mount state.

## Dependencies and Integration Points
It is used early in nightly base tests after build. It validates CLI argument parsing across command groups.

## Risks and Edge Cases
Using `&` backgrounds the command, so `$?` usually reports background launch success rather than the process exit code. This may make the test ineffective unless the shell fails before backgrounding. It does not use `wait`.

## Test Signals
Correct signals should be exit code `2` for each invalid command. A stronger test would remove backgrounding and assert directly.
