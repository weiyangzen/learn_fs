# sources/object-store/minio-mc/cmd/admin-user-svcacct-remove.go

## Purpose

`admin-user-svcacct-remove.go` implements `mc admin user svcacct remove` / `rm`, deleting a service account.

## Important APIs, Types, and Functions

`adminUserSvcAcctRemoveCmd` declares the command. `mainAdminUserSvcAcctRemove` calls `DeleteServiceAccount` and prints `acctMessage` with remove operation.

## Control Flow

The handler configures color, validates target and service-account access key, creates an admin client, sends the delete request, and prints success.

## State and Persistence Behavior

Remote service-account state is removed by the server. There is no local persistence.

## Dependencies and Integration Points

It depends on `newAdminClient`, `madmin.DeleteServiceAccount`, shared account output, global context, and the service-account command group.

## Risks and Edge Cases

There is no confirmation before deletion. Server-side behavior determines whether deleting an already removed or parent-owned account succeeds.

## Test Signals

Tests should cover arity, delete API call, failure message, and output operation.
