# sources/object-store/minio-mc/cmd/admin-user-svcacct-disable.go

## Purpose

`admin-user-svcacct-disable.go` implements `mc admin user svcacct disable`, turning a service account off.

## Important APIs, Types, and Functions

`adminUserSvcAcctDisableCmd` declares the command. `mainAdminUserSvcAcctDisable` sends `madmin.UpdateServiceAccountReq{NewStatus: "off"}`.

## Control Flow

The handler validates target and service account, creates an admin client, calls `UpdateServiceAccount`, and prints an `acctMessage` with disable operation.

## State and Persistence Behavior

The server persists the disabled status. No local files are changed.

## Dependencies and Integration Points

It uses shared service-account output from `admin-user-svcacct-add.go`, `madmin-go`, global context, and the service-account command group.

## Risks and Edge Cases

Status strings `"off"` and `"on"` are literal client-server contract values. There is no prior-state check or confirmation.

## Test Signals

Tests should assert arity, update payload, error propagation, and output message.
