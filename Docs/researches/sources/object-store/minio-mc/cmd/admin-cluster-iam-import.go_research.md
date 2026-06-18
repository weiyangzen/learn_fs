<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go

## Purpose
Implements cluster IAM import, restoring IAM info from a local zip file into a MinIO cluster.

## Important APIs, types, and functions
Defines a `cli.Command`, zip validation/syntax logic, main handler, and `iamImportInfo` output formatter. It uses madmin import result types to render successes, skips, removals, additions, and errors.

## Control flow
The command validates argument count, opens the zip file, creates a `zip.NewReader` to reject invalid archives, reopens the file for streaming, creates an admin client, calls `ImportIAMV2 with fallback to ImportIAM`, and prints structured results.

## State and persistence behavior
Reads a local zip backup and mutates server-side metadata/IAM state. No local output is persisted beyond terminal/JSON output.

## Dependencies and integration points
Depends on `klauspost/compress/zip`, madmin import APIs, console coloring, shared probe/fatal handling, and global output mode.

## Risks and test signals
Import is high impact: wrong target or stale backup can overwrite server metadata. Tests should cover invalid zip rejection, partial import error rendering, JSON output, and fallback behavior where present.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go -->
