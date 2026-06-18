# sources/object-store/minio-mc/cmd/admin-subnet.go

## Purpose

`admin-subnet.go` defines the hidden deprecated `mc admin subnet` group and bridges old SUBNET commands to the newer `mc support` namespace.

## Important APIs, Types, and Functions

`subnetHealthSubcommands` contains hidden health and register commands. `adminSubnetCmd` is the hidden top-level command. `mainAdminSubnet` reports deprecation to `mc support`. `adminHealthCmd` returns a hidden copy of the health command.

## Control Flow

The top-level command never performs health or registration itself. It delegates to subcommands when matched; otherwise it reports the deprecation target.

## State and Persistence Behavior

Only static command-tree state is defined.

## Dependencies and Integration Points

It integrates with the admin command tree, support diagnostics/register migration, `globalFlags`, and the command deprecation helper.

## Risks and Edge Cases

The copied command returned by `adminHealthCmd` can diverge if future code mutates fields after copy. Hidden command behavior must stay aligned with support command replacements.

## Test Signals

Useful tests verify hidden group and subcommands, bare group deprecation, and that `adminHealthCmd` returns a hidden command even if the base command changes.
