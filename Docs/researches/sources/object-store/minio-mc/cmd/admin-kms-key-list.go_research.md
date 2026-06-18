# sources/object-store/minio-mc/cmd/admin-kms-key-list.go

## Purpose
Implements `mc admin kms key list`, listing KMS master keys known to the MinIO server.

## Important APIs, types, and functions
`adminKMSKeyListCmd` declares the command. `mainAdminKMSKeyList` calls `ListKeys(globalContext, "*")`. `kmsKeysMsg` serializes JSON and fallback string output.

## Control flow
The command accepts exactly one target, initializes an admin client, lists keys with a wildcard, builds table rows and a plain key-name slice, then either prints JSON via `printMsg` or renders a go-pretty table titled `KMS Keys`.

## State and persistence behavior
The command is read-only. It observes remote KMS key metadata but does not cache it locally.

## Dependencies and integration points
It depends on `madmin-go` KMS list APIs, `go-pretty/table`, global JSON mode, console colors, and shared error handling.

## Risks and edge cases
The table numbering is local and starts at one. Ordering follows the server response. Empty key lists render an empty table, while JSON renders an empty array.

## Test signals
Tests should validate one-argument syntax, wildcard list calls, JSON payload fields, table rendering for zero and multiple keys, and error handling when KMS is unavailable.
