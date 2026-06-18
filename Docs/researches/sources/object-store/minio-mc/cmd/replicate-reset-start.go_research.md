# Research: sources/object-store/minio-mc/cmd/replicate-reset-start.go

## sources/object-store/minio-mc/cmd/replicate-reset-start.go

Purpose: implements `mc replicate resync start`, initiating re-replication of previously replicated objects for a remote target.

Important APIs and types: `replicateResyncStartCmd`, `checkReplicateResyncStartSyntax`, `replicateResyncMessage`, and `mainReplicateResyncStart`.

Control flow: syntax requires one target and `--remote-bucket`. Optional `--older-than` is parsed with `ParseDuration`, must include day/week/year-like units by string check, and must be nonzero. The handler creates a client, calls `ResetReplication(ctx, olderThan, remoteBucket)`, and prints target reset info.

State and persistence: mutates server-side replication resync/reset state for the bucket/target.

Dependencies and integration: uses MinIO replication resync APIs, custom duration parser, global context, and shared output.

Risks and tests: unit validation checks `strings.ContainsAny(olderThanStr, "dwy")`, but parser tests in this subset cover days/weeks, not years. Error handling passes possibly nil parse errors to `probe.NewError`. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-start.go -->
