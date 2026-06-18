# Research: sources/object-store/minio-mc/cmd/replicate-import.go

## sources/object-store/minio-mc/cmd/replicate-import.go

Purpose: implements `mc replicate import`, reading replication configuration JSON from stdin and applying it to a bucket.

Important APIs and types: `replicateImportCmd`, `checkReplicateImportSyntax`, `replicateImportMessage`, `readReplicationConfig`, and `mainReplicateImport`.

Control flow: syntax requires one target. `readReplicationConfig` decodes a `replication.Config` from `os.Stdin`. The handler creates a client, reads config, calls `SetReplication` with `ImportOption`, and prints success.

State and persistence: mutates bucket replication configuration on the target bucket.

Dependencies and integration: uses `colorjson` decoder, MinIO replication config APIs, shared fatal/output functions, and global context.

Risks and tests: stdin must be valid JSON matching the replication config structure. No validation of remote targets occurs in this file; server/client `SetReplication` must reject incompatible configs. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-import.go -->
