# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/write_test.go

Purpose: Exercises file write modes and validates GCS object attributes remain meaningful across append and overwrite operations.

Important APIs/types/functions: constants define temp names and content. `validateExtendedObjectAttributesNonEmpty` creates a storage client, stats the object, converts attributes to internal extended attributes, and rejects nil/empty results. `validateObjectAttributes` compares content type, component count, names, bucket, holds, sizes, hashes, media link, storage class, and mtime ordering. Tests cover append at EOF, write at start, `WriteAt` with `O_DIRECT`, create, append attribute changes, and truncate/write attribute changes.

Control flow: tests create a file under the operations prefix, perform one write variant, compare file contents, then fetch direct GCS attributes. Attribute tests snapshot attrs before and after mutation and validate expected size growth and stable metadata fields.

State/persistence: Writes persist to GCS; direct storage-client stat validates backend metadata rather than only mounted view. Zonal buckets expect `RAPID` storage class and tolerate missing media link.

Dependencies/integration: Uses Cloud Storage client, internal `gcs` and `storageutil` conversions, setup/client/operations helpers, and syscall flags.

Risks/test signals: Object name passed to storage stat omits randomized test directory suffixes, so it relies on shared package naming. Passing signals file writes flush content and preserve extended object metadata invariants.
