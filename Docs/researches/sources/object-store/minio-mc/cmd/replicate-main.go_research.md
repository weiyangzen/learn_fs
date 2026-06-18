# Research: sources/object-store/minio-mc/cmd/replicate-main.go

## sources/object-store/minio-mc/cmd/replicate-main.go

Purpose: parent command for server-side bucket replication management.

Important APIs and variables: `replicateSubcommands` lists add, update, list, status, resync/reset, export, import, remove, and backlog; `replicateCmd` defines the parent; `mainReplicate` handles unknown or missing subcommands.

Control flow: parent invocation delegates to `commandNotFound`, while subcommands own their handlers and validation.

State and persistence: no direct state mutation; subcommands can mutate remote replication configuration.

Dependencies and integration: registered in `appCmds`; depends on sibling command variables, including some not in this subset (`replicateUpdateCmd`, `replicateStatusCmd`).

Risks and tests: compile-time integration requires all referenced subcommand variables to exist. No direct tests for parent routing.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-main.go -->
