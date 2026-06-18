<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version_test.go -->
# sources/user-network-fs/rclone/cmd/version/version_test.go

## Purpose

`version_test.go` verifies that executing `rclone version` does not require a readable config file.

## Important APIs, Types, and Functions

`TestVersionWorksWithoutAccessibleConfigFile` creates a temporary config path, removes permissions on non-Windows systems, rewires `config.SetConfigPath`, nils `os.Stdout`, runs `cmd.Root` with `version`, and restores global state.

## Control Flow

The test simulates an unreadable config before invoking the Cobra root command. It asserts no panic and no returned error for the normal version path.

## State and Persistence Behavior

It mutates global config path, global stdout, and root command args, with defers restoring state. It creates and removes a temp file.

## Dependencies and Integration Points

It covers integration between the version command, config path handling, and root command execution.

## Risks and Test Signals

The test signals that version display must remain independent of config loading. It does not cover `--check`, `--deps`, network failures, or repeated root command state after execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version_test.go -->
