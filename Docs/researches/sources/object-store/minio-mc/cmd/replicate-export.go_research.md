# Research: sources/object-store/minio-mc/cmd/replicate-export.go

## sources/object-store/minio-mc/cmd/replicate-export.go

Purpose: implements `mc replicate export`, printing a bucket replication configuration.

Important APIs and types: `replicateExportCmd`, `checkReplicateExportSyntax`, `replicateExportMessage`, and `mainReplicateExport`.

Control flow: syntax requires one target. The handler creates a client, calls `GetReplication`, and prints a message. Human output prints only the replication config JSON or a no-config message; JSON mode wraps it with operation/status/url fields.

State and persistence: read-only object-store operation.

Dependencies and integration: uses MinIO replication config type, `colorjson` for marshaling, shared output and fatal helpers.

Risks and tests: human output is JSON even when global JSON mode is false, which is intentional for export but different from most commands. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-export.go -->
