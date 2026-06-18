# sources/object-store/minio-mc/cmd/admin-kms-key.go

## Purpose
Defines the `mc admin kms key` command group for KMS master key management.

## Important APIs, types, and functions
`adminKMSKeySubcommands` registers create, status, and list. `adminKMSKeyCmd` declares the group. `mainAdminKMSKey` delegates invalid invocations to `commandNotFound`.

## Control flow
No KMS operation is implemented directly. The file routes recognized subcommands and otherwise invokes the common command-not-found behavior.

## State and persistence behavior
No state is read or written here. Remote key state is handled by subcommand files.

## Dependencies and integration points
It depends on `minio/cli`, global flags, `setGlobalsFromContext`, sibling KMS command variables, and the parent `admin kms` group.

## Risks and edge cases
Registration drift is the main risk; new key operations must be added to this list. Hidden help behavior means not-found UX depends on shared infrastructure.

## Test signals
Tests should verify the key subcommands are reachable and that a bare or unknown `mc admin kms key` invocation routes to shared help/not-found behavior.
