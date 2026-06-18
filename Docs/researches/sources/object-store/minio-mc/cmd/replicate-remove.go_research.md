# Research: sources/object-store/minio-mc/cmd/replicate-remove.go

## sources/object-store/minio-mc/cmd/replicate-remove.go

Purpose: implements `mc replicate remove`/`rm`, removing one replication rule or all replication configuration.

Important APIs and types: `replicateRemoveCmd`, `checkReplicateRemoveSyntax`, `replicateRemoveMessage`, and `mainReplicateRemove`.

Control flow: syntax requires one target. `--all` and `--force` must appear together; otherwise a non-empty `--id` is required. The handler fetches replication config. All+force calls `RemoveReplication`; single-rule mode finds the destination ARN for that rule, calls `SetReplication(RemoveOption)`, then removes the corresponding remote target with admin API.

State and persistence: mutates replication rules and possibly remote target configuration on the source bucket.

Dependencies and integration: uses MinIO replication options, `madmin.RemoveRemoteTarget`, source bucket extraction, shared output.

Risks and tests: if the rule ID is not found, `removeArn` remains empty but the code still attempts rule removal and remote-target removal. Output string misses a space before "removed". No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-remove.go -->
