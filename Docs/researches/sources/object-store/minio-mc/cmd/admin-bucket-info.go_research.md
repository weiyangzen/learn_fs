<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-info.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-info.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket info`. It keeps the old CLI entry point registered while directing users to `mc stat`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc stat` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-info.go -->
