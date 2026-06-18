# sources/object-store/minio-mc/cmd/admin-user-svcacct-enable.go

## Purpose

`admin-user-svcacct-enable.go` implements `mc admin user svcacct enable`, turning a service account on.

## Important APIs, Types, and Functions

`adminUserSvcAcctEnableCmd` declares the command. `mainAdminUserSvcAcctEnable` sends `madmin.UpdateServiceAccountReq{NewStatus: "on"}`.

## Control Flow

The handler validates two args, creates an admin client, updates account status, and prints a service-account success message.

## State and Persistence Behavior

Remote IAM service-account status is persisted by the server. The command writes no local state.

## Dependencies and Integration Points

It depends on `madmin.UpdateServiceAccount`, shared `acctMessage`, console coloring, and global context.

## Risks and Edge Cases

There is no validation of account type beyond server response. Status string values are not typed constants in this file.

## Test Signals

Tests should cover status payload `"on"`, syntax failures, and message rendering.
