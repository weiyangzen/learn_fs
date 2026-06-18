# sources/user-network-fs/rclone/cmd/serve/docker/options_test.go

## Purpose

This file tests Docker volume option classification and parsing.

## Important APIs, Types, and Functions

`TestApplyOptions` constructs a minimal `Volume` with mount point, driver, mount point object, and request map, then calls `applyOptions`.

## Control Flow

The happy path mixes remote, persist, mount-type, backend, mount, and VFS options with dashes, underscores, and leading `--`, then asserts the generated fs string and parsed option fields. Error cases verify invalid mount option values, invalid VFS option values, and unsupported backend option rejection.

## State and Persistence Behavior

The test mutates only an in-memory `Volume`.

## Dependencies and Integration Points

It depends on local backend registration, mountlib option metadata, VFS option metadata, rclone duration parsing, and testify.

## Risks and Test Signals

It gives good coverage for normalization and routing of flat options. It does not test `type` without `remote`, `path` override, configured named remotes, prefixed non-local backend options, or persistence restrictions.
