# sources/object-store/minio-mc/cmd/admin-service-freeze.go

## Purpose
Implements the hidden `mc admin service freeze` command, sending a request to freeze S3 API calls on a MinIO cluster.

## Important APIs, types, and functions
`adminServiceFreezeCmd` defines the hidden command. `serviceFreezeCommand` formats success output. `checkAdminServiceFreezeSyntax` requires a single target, and `mainAdminServiceFreeze` calls `ServiceFreezeV2`.

## Control flow
The handler validates one alias, sets success/failure colors, creates an admin client, invokes the server freeze API, and prints a success message with the server URL.

## State and persistence behavior
The persistent operational effect is remote: S3 API calls are frozen on the target MinIO cluster according to server semantics. No local state is written.

## Dependencies and integration points
It integrates the admin service API, global context, hidden command registration under service management, `probe` error handling, `colorjson`, and console output.

## Risks and edge cases
The command is hidden on purpose and can disrupt cluster availability. There is no confirmation prompt or unfreeze path in this file. The comment contains a typo in `service`.

## Test signals
Tests should cover hidden metadata, syntax validation, admin client creation, freeze API failure, JSON output, and human success output.
