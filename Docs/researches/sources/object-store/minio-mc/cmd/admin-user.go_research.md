# sources/object-store/minio-mc/cmd/admin-user.go

## Purpose

`admin-user.go` defines the `mc admin user` command group for user, service-account, and STS account management.

## Important APIs, Types, and Functions

`adminUserSubcommands` contains add, disable, enable, remove, list, info, policy, svcacct, and sts. `adminUserCmd` defines the group. `mainAdminUser` calls `commandNotFound`.

## Control Flow

The group command only handles missing or invalid subcommands. All IAM operations are delegated to subcommands.

## State and Persistence Behavior

Only command registration state is declared.

## Dependencies and Integration Points

It integrates the user family into the admin command tree and pulls in subcommands declared across sibling files.

## Risks and Edge Cases

The code comment says "admin config" rather than "admin user", which is documentation drift only. Registration order affects help and completion.

## Test Signals

Tests should assert subcommand presence, aliases on child commands, and bare group command-not-found behavior.
