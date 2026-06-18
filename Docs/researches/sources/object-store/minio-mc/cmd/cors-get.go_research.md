# sources/object-store/minio-mc/cmd/cors-get.go

Purpose: Implements `mc cors get` for retrieving a bucket CORS configuration.

Important APIs/types/functions: `corsGetCmd`, `checkCorsGetSyntax`, and `mainCorsGet`.

Control flow: The command requires exactly one `ALIAS/BUCKET` argument, initializes colors, creates a client with `newClient`, calls `GetBucketCors(globalContext)`, maps nil config to `not found`, and prints a shared `corsMessage`.

State and persistence: Does not persist local state. Reads remote bucket CORS configuration from object storage.

Dependencies/integration: Uses MinIO cli, console color, `newClient`, `fatalIf`, `printMsg`, and `corsMessage` from `cors-set.go`.

Risks: Only syntax validation is argument count; bucket/path validity is deferred to client creation and server response. Nil config is not treated as an error.

Test signals: No direct tests in this subset.
