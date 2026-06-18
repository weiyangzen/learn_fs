<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go -->
# sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go

## Purpose

`e2e_test.go` runs integration tests against real `git-annex`, the rclone binary on PATH, and local rclone config to verify the built-in git-annex remote works and remains layout-compatible with `git-annex-remote-rclone`.

## Important APIs, Types, and Functions

Helpers verify rclone binary version, count remote files, search contents, create an isolated HOME/PATH/repo context, install the `git-annex-remote-rclone-builtin` symlink, write rclone config, and run commands in the temp repo. `skipE2eTestIfNecessary` gates short mode, fstest remotes, OS support, rclone version, and `git-annex` availability. Tests cover `testremote`, migration from externaltype `rclone`, and cross-remote layout compatibility for all layout modes.

## Control Flow

Each test creates a temp git-annex repository, initializes remotes with layout parameters, writes annexed files, runs copy/fsck/drop workflows, and checks local remote storage state.

## State and Persistence Behavior

Tests create temp repositories, configs, symlinks, git commits, and local remote storage. Cleanup is temp-dir based with explicit annex drops for read-only objects.

## Dependencies and Integration Points

They integrate with external `git`, `git-annex`, `git-annex-remote-rclone`, rclone CLI, local backend config, build tags, and layout modes.

## Risks and Test Signals

Signals are high-value end-to-end compatibility. Risks include environmental flakiness, PATH version mismatch, unsupported Windows HOME semantics, missing external tools, parallel temp repo load, and tests skipped in common developer setups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go -->
