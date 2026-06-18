# Research: sources/object-store/minio-mc/cmd/replicate-list.go

## sources/object-store/minio-mc/cmd/replicate-list.go

Purpose: implements `mc replicate list`/`ls`, displaying bucket replication rules and resolving remote target endpoints.

Important APIs and types: `replicateListCmd`, `checkReplicateListSyntax`, `printReplicateListHeader`, `replicateListMessage`, and `mainReplicateList`.

Control flow: the handler fetches replication config, errors if empty, prints a header in human mode, lists remote targets through admin API, optionally filters rules by `--status`, and prints each rule. String output resolves destination ARN to bucket and endpoint when possible, then shows rule ID, priority, ARN, optional prefix/tags/storage class.

State and persistence: read-only remote calls.

Dependencies and integration: uses `Client.GetReplication`, `madmin.ListRemoteTargets`, MinIO replication rule types, ARN parsing, shared color/output utilities.

Risks and tests: `--status` accepts any string and only filters by case-insensitive equality; invalid values silently produce no rows. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-list.go -->
