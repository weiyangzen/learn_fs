# sources/object-store/minio-mc/cmd/admin-service.go

## Purpose

`admin-service.go` is the command group definition for `mc admin service`. It wires service lifecycle subcommands into the admin command tree.

## Important APIs, Types, and Functions

`adminServiceSubcommands` contains restart, stop, unfreeze, and freeze commands. `adminServiceCmd` is a `cli.Command` with global flags and no help subcommand. `mainAdminService` delegates unknown command handling to `commandNotFound`.

## Control Flow

The top-level command does not perform service operations itself. The CLI dispatcher invokes a subcommand when present; otherwise `mainAdminService` reports valid subcommands.

## State and Persistence Behavior

This file owns only static command registration state and has no persistence.

## Dependencies and Integration Points

It depends on sibling command variables, `setGlobalsFromContext`, `globalFlags`, and `commandNotFound`. It integrates with the root admin command tree elsewhere in the package.

## Risks and Edge Cases

Registration order affects help display and command discovery. Hidden subcommands such as stop still exist in the slice and may be reachable by name.

## Test Signals

Command-tree tests should confirm that visible subcommands are registered, hidden subcommands remain hidden where expected, and bare `mc admin service` reports command-not-found help rather than performing an action.
