# sources/object-store/minio-mc/cmd/admin-top.go

## Purpose

`admin-top.go` groups `mc admin top` subcommands that provide top-like MinIO statistics, with current subcommands redirected to support equivalents.

## Important APIs, Types, and Functions

`adminTopSubcommands` contains API and locks commands. `adminTopCmd` defines the group. `mainAdminTop` calls `commandNotFound`.

## Control Flow

The group action is only used for invalid or missing subcommands. Real behavior is delegated to `adminTopAPICmd` or `adminTopLocksCmd`.

## State and Persistence Behavior

Only static command metadata is defined.

## Dependencies and Integration Points

It integrates with the admin command tree, top API/locks subcommands, global flags, and command-not-found handling.

## Risks and Edge Cases

Subcommand deprecations must remain synchronized with support command implementations. Parent command help can expose or hide deprecated children depending on their own visibility flags.

## Test Signals

Tests should verify subcommand list composition and bare group behavior.
