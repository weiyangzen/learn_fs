# sources/object-store/minio-mc/cmd/admin-top-api.go

## Purpose

`admin-top-api.go` preserves the hidden deprecated `mc admin top api` command and redirects users to `mc support top api`.

## Important APIs, Types, and Functions

`adminTopAPIFlags` defines legacy filters for API name, path, node, and errors. `adminTopAPICmd` is hidden and bound to `mainAdminTopAPI`, which calls `deprecatedError`.

## Control Flow

The command does not contact the server. When invoked, it emits a deprecation error with the support command replacement.

## State and Persistence Behavior

No local or remote state is changed.

## Dependencies and Integration Points

The file integrates with `admin-top.go`, global flags, CLI usage handling, and the support namespace migration.

## Risks and Edge Cases

Legacy flags remain declared even though the handler only reports deprecation. Scripts relying on the old command must migrate to support top.

## Test Signals

Tests should confirm hidden status, flag names retained for parsing, and replacement message content.
