<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/environment_test.go -->
# sources/user-network-fs/rclone/cmdtest/environment_test.go

## Purpose

`environment_test.go` is an end-to-end suite for rclone environment-variable parsing and precedence.

## Important APIs, Types, and Functions

The sole test uses the cmdtest harness to run actual rclone commands with controlled `RCLONE_*` variables. It validates non-backend flags, backend remote names, option precedence, alias/reference behavior, JSON logging, and string-array filter variables.

## Control Flow

The test creates local data and a config, invokes child rclone processes with different semicolon-delimited environments, and inspects command output. It covers global flags such as `RCLONE_MAX_DEPTH`, conflict handling for quiet/log-level, default help text changes, command-line overrides, remote names containing hyphens/underscores, symlink handling precedence across connection string, CLI flag, remote env, backend env, generic env, and config file values.

## State and Persistence Behavior

All data and config live under a test temp directory. The test creates symlinks when supported, rewrites `myLocal` and `myAlias` remotes, and relies on child process isolation for environment changes.

## Dependencies and Integration Points

It integrates with config creation, local and alias backends, environment-to-config conversion, flag default rendering, logging formats, JSON logging, and filter dumping.

## Risks and Test Signals

This is a high-value regression suite for option precedence. Risks include OS symlink policy, output-format brittleness, semicolon environment encoding, and global config interactions. It does not cover every backend option type, but it exercises string arrays and key precedence layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/environment_test.go -->
