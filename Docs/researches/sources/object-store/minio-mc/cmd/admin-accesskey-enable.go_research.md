<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-enable.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-enable.go

## Purpose
Registers the MinIO admin access key enable command. The file is a thin CLI surface for a shared access-key implementation and reenables a disabled access key.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `enableDisableAccesskey(ctx, true)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-enable.go -->
