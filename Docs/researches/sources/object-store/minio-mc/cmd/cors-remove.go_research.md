# sources/object-store/minio-mc/cmd/cors-remove.go

Purpose: Implements `mc cors remove` for deleting bucket CORS configuration.

Important APIs/types/functions: `corsRemoveCmd`, `checkCorsRemoveSyntax`, and `mainCorsRemove`.

Control flow: Requires one bucket argument, initializes a client, calls `DeleteBucketCors(globalContext)`, and prints success through `corsMessage`.

State and persistence: Mutates remote bucket configuration; no local persistence.

Dependencies/integration: Uses shared CLI/global setup, `newClient`, `fatalIf`, and `printMsg`.

Risks: Destructive operation has no confirmation flag in this file. Errors from the remote API are fatal.

Test signals: No direct tests.
