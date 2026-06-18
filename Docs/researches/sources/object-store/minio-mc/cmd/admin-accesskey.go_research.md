<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey.go

## Purpose
Command group registration for `mc admin accesskey`, collecting all access-key management subcommands.

## Important APIs, types, and functions
`adminAccesskeySubcommands` lists list, remove, info, create, edit, enable, disable, and STS revoke commands. `adminAccesskeyCmd` registers the group and `mainAdminAccesskey` handles missing subcommands.

## Control flow
CLI dispatch enters the group; if no valid subcommand is provided, `commandNotFound` reports usage. Real behavior lives in subcommand files.

## State and persistence behavior
No state directly. Subcommands mutate or read server IAM state.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flags, and all access-key subcommand variables.

## Risks and test signals
Subcommand ordering affects help output. Compile catches missing command variables; CLI tests should verify unknown subcommand handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey.go -->
