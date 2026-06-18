<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config.go -->
# sources/object-store/minio-mc/cmd/admin-config.go

## Purpose
CLI command group registration for `mc admin config`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config.go -->
