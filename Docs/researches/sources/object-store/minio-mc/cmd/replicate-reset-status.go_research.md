# Research: sources/object-store/minio-mc/cmd/replicate-reset-status.go

## sources/object-store/minio-mc/cmd/replicate-reset-status.go

Purpose: implements `mc replicate resync status`, showing replication reset progress for all or one remote target.

Important APIs and types: `replicateResyncStatusCmd`, `checkreplicateResyncStatusSyntax`, `replicateResyncStatusMessage`, and `mainreplicateResyncStatus`.

Control flow: syntax requires one target. The handler creates a client, calls `ReplicationResyncStatus(ctx, remoteBucket)`, and prints the message. String output shows a warning when no status exists; otherwise it formats each target ARN, status, replicated size/count, and failed size/count with `PrettyTable`.

State and persistence: read-only server-side resync status.

Dependencies and integration: uses replication resync info types, humanize formatting, shared color themes, `PrettyTable`, and `printMsg`.

Risks and tests: function names use lowercase `replicate` after `main`, which is legal but inconsistent. The "Failed" row is colorized with the replicated theme index in one call. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-status.go -->
