# sources/object-store/minio-mc/cmd/admin-service-stop.go

## Purpose

`admin-service-stop.go` implements the hidden `mc admin service stop` command that stops a MinIO cluster through the admin API.

## Important APIs, Types, and Functions

`adminServiceStopCmd` is a hidden `cli.Command` wired to `mainAdminServiceStop`. `serviceStopMessage` supplies plain text and JSON output. `checkAdminServiceStopSyntax` accepts one or two arguments, though the handler uses only the first target.

## Control Flow

The handler validates arguments, configures success color, extracts the target alias, builds an admin client, calls `client.ServiceStopV2(globalContext)`, and prints a success message.

## State and Persistence Behavior

There is no local persistence. The command mutates remote cluster process state by sending a stop request. Output state is limited to the target URL and status string.

## Dependencies and Integration Points

The file depends on `newAdminClient`, `madmin.AdminClient.ServiceStopV2`, `fatalIf`, `printMsg`, global flags, color JSON, and console colorization. It is registered by `admin-service.go`.

## Risks and Edge Cases

The command is intentionally hidden because stopping a cluster is disruptive. The syntax checker allows a second argument that is ignored, which can hide accidental extra input. There is no fallback to an older stop API in this file.

## Test Signals

Tests should assert hidden command registration, syntax behavior for zero and three arguments, success message encoding, and that `ServiceStopV2` is invoked exactly once for the resolved alias.
