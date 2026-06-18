# sources/object-store/minio-mc/cmd/admin-subnet-health.go

## Purpose

`admin-subnet-health.go` preserves the hidden deprecated `mc admin subnet health` command and redirects users toward `mc support diag`.

## Important APIs, Types, and Functions

`adminSubnetHealthCmd` is a hidden `cli.Command` using `supportDiagFlags`. `mainSubnetHealth` builds a replacement command string. It uses `set.CreateStringSet` to detect boolean flag values.

## Control Flow

The handler starts with `mc support diag`, appends original positional args, then iterates command flags that were set. It maps deprecated `--offline` to `--airgap`, quotes non-boolean flag values, and calls `deprecatedError` with the new command.

## State and Persistence Behavior

There is no state mutation or persistence. The command exists only for compatibility messaging.

## Dependencies and Integration Points

It integrates with support diagnostic flags, `deprecatedError`, MinIO set utilities, and the hidden subnet group.

## Risks and Edge Cases

The generated replacement command is a display string, not shell-escaped robustly for every possible value. Boolean detection uses string values `"true"` and `"false"`, so unusual flag renderings could be quoted differently.

## Test Signals

Tests should verify hidden registration, `offline` to `airgap` translation, omission of unset flags, quoting of string values, and the final replacement string for common diagnostic options.
