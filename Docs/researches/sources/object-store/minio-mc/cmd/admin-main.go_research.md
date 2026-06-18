# sources/object-store/minio-mc/cmd/admin-main.go

## Purpose
Defines the root `mc admin` command and registers the full MinIO server administration command set.

## Important APIs, types, and functions
`adminCmdSubcommands` lists service, update, info, inspect, user, group, policy, replicate, idp, config, decommission, heal, prometheus, kms, health, subnet, bucket, tier, speedtest, profile, scanner, top, trace, console, cluster, rebalance, logs, and accesskey commands. Constants `dot`, `check`, and `dateTimeFormatFilename` provide shared display symbols and filename timestamp format.

## Control flow
The root command invokes `mainAdmin` only when no subcommand handles the invocation. `mainAdmin` delegates to `commandNotFound`, while recognized subcommands own all operational flow.

## State and persistence behavior
This file has no state mutation. It only composes the admin CLI surface and shared flags.

## Dependencies and integration points
It is the integration point for all admin subcommand variables in the `cmd` package and for global option initialization via `setGlobalsFromContext`.

## Risks and edge cases
The command list is a large manual registry; omissions make commands unreachable. Hidden or deprecated commands remain in the namespace for compatibility. Display constants are reused by multiple status formatters.

## Test signals
Tests should verify top-level registration of key command families, correct command-not-found behavior, and that shared flags are present on the root admin command.
