# sources/object-store/minio-mc/cmd/admin-user-svcacct.go

## Purpose

`admin-user-svcacct.go` defines the `mc admin user svcacct` command group for service-account management.

## Important APIs, Types, and Functions

`adminUserSvcAcctSubcommands` includes add, list, remove, info, edit/set, enable, and disable. `adminUserSvcAcctCmd` defines the group command. `mainAdminUserSvcAcct` delegates invalid usage to `commandNotFound`.

## Control Flow

No service-account operation happens at the group level. The CLI dispatches to subcommands; otherwise the group action reports valid subcommands.

## State and Persistence Behavior

Only static command metadata is defined.

## Dependencies and Integration Points

It integrates with the admin user command group, sibling service-account command files, global flags, and shared command-not-found behavior.

## Risks and Edge Cases

Subcommand registration order affects help output. The `edit` command also has alias `set`, so completion and help must account for both names.

## Test Signals

Tests should verify subcommand composition and bare group behavior.
