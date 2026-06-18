# sources/object-store/minio-mc/cmd/admin-user-svcacct-set.go

## Purpose

`admin-user-svcacct-set.go` implements `mc admin user svcacct edit` and alias `set`, updating mutable fields on a service account.

## Important APIs, Types, and Functions

`adminUserSvcAcctSetFlags` includes secret key, policy, name, description, and expiry. `adminUserSvcAcctSetCmd` binds both `edit` and `set`. `mainAdminUserSvcAcctSet` builds `madmin.UpdateServiceAccountReq`.

## Control Flow

The handler validates target and service account, reads optional fields, creates an admin client, reads optional policy bytes, parses optional expiry using shared `supportedTimeFormats` and local timezone, builds an update request with only provided values, sends `UpdateServiceAccount`, and prints an edit success message.

## State and Persistence Behavior

The server persists updated service-account fields, policy, secret, and expiration. The client reads a local policy file but writes no local files.

## Dependencies and Integration Points

It depends on shared time formats from `admin-user-svcacct-add.go`, `madmin.UpdateServiceAccountReq`, file IO for policy bytes, and shared account output.

## Risks and Edge Cases

Unlike add, this file does not parse or reject empty policy documents client-side; validation is left to the server. There is no way to clear expiration except by server semantics for nil or absent fields. Local timezone affects expiry interpretation.

## Test Signals

Tests should cover each optional field independently, invalid policy path, invalid expiry, alias name `set`, nil versus non-nil expiration pointer, and update payload contents.
