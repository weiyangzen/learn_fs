# Research: sources/object-store/minio-mc/cmd/replicate-reset-main.go

## sources/object-store/minio-mc/cmd/replicate-reset-main.go

Purpose: parent command for replication resync/reset operations.

Important APIs and variables: `replicateResyncSubcommands` lists `start` and `status`; `replicateResyncCmd` defines `mc replicate resync`, alias `reset`, and hidden aliases; `mainReplicateResync` handles parent invocation.

Control flow: invoking the parent without a valid subcommand delegates to `commandNotFound`; subcommands perform actual resync work.

State and persistence: no direct mutation in the parent. `start` mutates server-side resync state; `status` reads it.

Dependencies and integration: included under `replicateSubcommands` in `replicate-main.go`.

Risks and tests: alias compatibility is handled by CLI metadata. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-main.go -->
