# sources/object-store/minio-mc/cmd/admin-tier-main.go

## Purpose

`admin-tier-main.go` defines the hidden deprecated `mc admin tier` command group and redirects users to `mc ilm tier`.

## Important APIs, Types, and Functions

`adminTierCmd` is a hidden `cli.Command` with `adminTierDepCmds` as subcommands. `mainAdminTier` emits the deprecation target.

## Control Flow

The top-level action runs only for a bare or invalid group invocation. Subcommands dispatch through the hidden command definitions in `admin-tier-deprecated.go`.

## State and Persistence Behavior

Only static command registration is present.

## Dependencies and Integration Points

The file depends on legacy subcommand metadata, `deprecatedError`, `globalFlags`, and admin command registration.

## Risks and Edge Cases

Because subcommands are still registered, legacy automation may still reach hidden tier handlers. Any migration policy must consider both the top-level deprecation and hidden subcommand execution.

## Test Signals

Tests should assert hidden group status, replacement text, and correct subcommand attachment.
