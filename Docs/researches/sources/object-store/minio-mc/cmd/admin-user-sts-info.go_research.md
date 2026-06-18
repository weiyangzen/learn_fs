# sources/object-store/minio-mc/cmd/admin-user-sts-info.go

## Purpose

`admin-user-sts-info.go` defines `mc admin user sts` and implements `mc admin user sts info` for temporary STS account inspection.

## Important APIs, Types, and Functions

`adminUserSTSAcctCmd` groups STS subcommands. `adminUserSTSAcctInfoCmd` supports `--policy`. `mainAdminUserSTSAcctInfo` calls `TemporaryAccountInfo` and reuses `acctMessage` output from service-account code.

## Control Flow

The group command delegates unknown subcommands. The info handler validates target and STS account, fetches account info, optionally parses and pretty-prints the embedded policy to stdout, otherwise prints an `acctMessage` with status, parent user, implied policy flag, policy raw JSON, and expiration.

## State and Persistence Behavior

The command reads temporary account state and writes stdout only. It does not mutate IAM state.

## Dependencies and Integration Points

It integrates with `madmin` temporary account APIs, shared service-account message types, MinIO policy parsing, and the admin user command group.

## Risks and Edge Cases

The error message refers to service accounts even though the command is for STS accounts. `--policy` fails if no embedded policy exists, even if parent policy applies. Raw policy is passed as `json.RawMessage`.

## Test Signals

Tests should cover no-policy and embedded-policy accounts, parse errors, implied policy output, expiration formatting, and group command-not-found behavior.
