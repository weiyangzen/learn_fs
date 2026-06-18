<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go

## Purpose
Implements cluster bucket export, downloading bucket metadata from a MinIO server into a local zip file for backup or migration.

## Important APIs, types, and functions
Defines a `cli.Command`, syntax checker for `target/[bucket]`, and main handler. The handler creates an admin client, calls `ExportBucketMetadata`, writes a temp file, backs up any existing destination, renames into place, chmods to `0600`, and prints text or JSON.

## Control flow
After syntax validation and alias normalization, the command streams server response to a temp file. Existing destination files are moved aside with a timestamp before the temp file is atomically moved into the final path.

## State and persistence behavior
Writes local backup zip files and backup copies of prior outputs. Server state is read-only. Output permissions are tightened to avoid world-readable metadata.

## Dependencies and integration points
Depends on madmin export APIs, filesystem helpers such as `moveFile`, global JSON mode, console coloring, and MinIO probe errors.

## Risks and test signals
Path construction from aliases can create surprising local paths; export contains sensitive metadata. Tests should cover existing destination backup, custom output where supported, permission mode, JSON output, and stream copy failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go -->
