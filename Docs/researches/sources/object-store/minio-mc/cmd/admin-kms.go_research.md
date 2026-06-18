# sources/object-store/minio-mc/cmd/admin-kms.go

## Purpose
Defines the top-level `mc admin kms` command group for KMS management operations.

## Important APIs, types, and functions
`adminKMSSubcommands` currently contains `adminKMSKeyCmd`. `adminKMSCmd` registers the group, and `mainAdminKMS` delegates unknown subcommands to `commandNotFound`.

## Control flow
The file acts as a namespace router. All behavior is delegated to `mc admin kms key ...` commands.

## State and persistence behavior
No local or remote state is accessed directly.

## Dependencies and integration points
It integrates with the top-level admin command, `minio/cli`, global flags, and the KMS key command group.

## Risks and edge cases
Future KMS subcommands require updates here. Since only one subcommand exists, users invoking `kms` directly rely on the quality of command-not-found/help output.

## Test signals
Registration tests should confirm `mc admin kms key` is reachable and bare or invalid `kms` invocations produce the common not-found path.
