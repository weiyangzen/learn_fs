# sources/object-store/minio-mc/cmd/admin-subnet-register.go

## Purpose

`admin-subnet-register.go` preserves the hidden deprecated `mc admin subnet register` command and points users to `mc support register`.

## Important APIs, Types, and Functions

`adminSubnetRegisterCmd` defines the hidden command. `mainAdminRegister` calls `deprecatedError("mc support register")`.

## Control Flow

The CLI invokes the handler for the deprecated command; the handler emits the replacement-command error and returns.

## State and Persistence Behavior

No local or remote state is changed.

## Dependencies and Integration Points

It depends on `deprecatedError`, `setGlobalsFromContext`, and registration in `admin-subnet.go`.

## Risks and Edge Cases

Because the command is hidden but still registered, automation using the old command will receive a deprecation failure rather than silently performing registration.

## Test Signals

Tests should confirm hidden status, replacement message content, and that no admin/support API client is created.
