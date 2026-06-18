# sources/object-store/minio-mc/cmd/admin-user-svcacct-info.go

## Purpose

`admin-user-svcacct-info.go` implements `mc admin user svcacct info`, showing service-account metadata and optionally its embedded policy.

## Important APIs, Types, and Functions

`adminUserSvcAcctInfoFlags` defines `--policy`. `mainAdminUserSvcAcctInfo` calls `InfoServiceAccount`, parses optional policy with `policy.ParseConfig`, and prints `acctMessage`.

## Control Flow

The handler validates target and service account, fetches account info, and branches on `--policy`. Policy mode requires a non-empty embedded policy and writes indented JSON to stdout. Normal mode prints access key, friendly name, description, status, parent user, implied policy flag, raw policy, and expiration.

## State and Persistence Behavior

The command reads remote service-account state only.

## Dependencies and Integration Points

It integrates with `madmin` service-account APIs, shared `acctMessage`, policy parsing, color JSON, and standard output.

## Risks and Edge Cases

`--policy` fails when the account relies on parent policy. Raw policy JSON is included in message output, so invalid server-side policy JSON could affect JSON encoding.

## Test Signals

Tests should cover policy/no-policy paths, parse errors, implied policy rendering, nil expiration, and JSON output.
