# sources/object-store/minio-mc/cmd/admin-user-svcacct-list.go

## Purpose

`admin-user-svcacct-list.go` implements `mc admin user svcacct list` / `ls`, listing service accounts for a target MinIO or LDAP account.

## Important APIs, Types, and Functions

`adminUserSvcAcctListCmd` declares the command. `mainAdminUserSvcAcctList` calls `ListServiceAccounts`, prints a table header in non-JSON mode, normalizes sentinel expiration values, and emits `acctMessage` rows.

## Control Flow

The handler validates target and parent account, creates an admin client, fetches the account list, prints a header if entries exist and output is not JSON, iterates accounts, converts `timeSentinel` expiration to nil, and prints each row. Empty non-JSON output prints "No service accounts found".

## State and Persistence Behavior

The command reads remote IAM state only.

## Dependencies and Integration Points

It uses shared `acctMessage`, `timeSentinel` from elsewhere in the package, `madmin.ListServiceAccounts`, and console table helpers.

## Risks and Edge Cases

The command requires a parent account and cannot list all service accounts globally. Empty results produce no JSON message. The typo "services accounts" is present in usage text.

## Test Signals

Tests should verify empty output behavior, header suppression in JSON mode, sentinel expiration handling, and row formatting.
