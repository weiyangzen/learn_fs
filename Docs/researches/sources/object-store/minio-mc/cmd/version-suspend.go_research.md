## sources/object-store/minio-mc/cmd/version-suspend.go

Purpose: implements `mc version suspend`, changing an existing bucket's versioning state to suspended. Key surfaces are `versionSuspendCmd`, `versionSuspendMessage`, `checkVersionSuspendSyntax`, and `mainVersionSuspend`.

Control flow requires exactly one target, constructs a client, and calls `client.SetVersion(ctx, "suspend", nil, false)`, then prints a success message. State is remote bucket versioning metadata. Dependencies include cli, console, colorjson, `probe`, and the client abstraction. Integration points are the top-level `version` command and S3/MinIO versioning APIs. Risks include server-side constraints not visible here, such as object lock or replication preventing suspension; this layer relies on the server/client error. No direct tests are included.
