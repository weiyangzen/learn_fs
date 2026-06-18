# sources/object-store/minio-mc/cmd/admin-tier-deprecated.go

## Purpose

`admin-tier-deprecated.go` declares the hidden legacy `mc admin tier` subcommands for remote tier targets. The actual handlers are shared with newer ILM tier functionality, while this file keeps old help text and compatibility wiring.

## Important APIs, Types, and Functions

`adminTierDepCmds` includes `info`, `ls`, `add`, `edit`, `verify`, and `rm`. Each command is hidden, uses `setGlobalsFromContext`, and points to handlers such as `mainAdminTierInfo`, `mainAdminTierAdd`, and `mainAdminTierRm`. Add/edit append specialized tier flags from sibling ILM tier code.

## Control Flow

There is no executable business logic beyond command dispatch metadata. If a hidden legacy subcommand is invoked, the CLI dispatcher calls the shared handler. Bare `mc admin tier` is handled by `admin-tier-main.go`.

## State and Persistence Behavior

The file defines static CLI metadata only. Remote tier configuration persistence is performed by shared handler functions declared elsewhere.

## Dependencies and Integration Points

It integrates legacy admin-tier names with the ILM tier implementation, global flags, custom help templates, and handler functions from other files.

## Risks and Edge Cases

The hidden commands can continue to modify tier state through shared handlers despite the top-level namespace being deprecated. Help examples must stay consistent with actual flag names. Add/edit flag slices are shared dependencies and can affect this legacy namespace.

## Test Signals

Command-tree tests should verify hidden status, correct handler binding for each legacy subcommand, expected flag composition for add/edit, and no accidental visibility in normal help.
