# Research: sources/object-store/minio-mc/cmd/rb-main.go

## sources/object-store/minio-mc/cmd/rb-main.go

Purpose: implements `mc rb`, removing buckets or filesystem directory hierarchies, with force and site-wide safety controls.

Important APIs and functions: `rbCmd`, `removeBucketMessage`, `checkRbSyntax`, `listBucketsURLs`, `deleteBucket`, `isS3NamespaceRemoval`, and `mainRemoveBucket`.

Control flow: syntax requires targets and blocks alias-wide object-store namespace removal unless both `--force` and `--dangerous` are set. `mainRemoveBucket` stats each target, checks emptiness, requires force for non-empty targets, expands namespace removals into buckets, and calls `deleteBucket`. `deleteBucket` streams recursive listed contents to `Client.Remove`, then removes the bucket, retrying force removal on `BucketNotEmpty`.

State and persistence: destructive remote or filesystem mutation. Can delete all buckets under an alias when explicitly forced and marked dangerous.

Dependencies and integration: uses `Client.List`, `Client.Remove`, `Client.RemoveBucket`, S3 error conversion, URL alias helpers, and shared fatal/output functions.

Risks and tests: highly destructive path with safety checks dependent on URL classification. Listing errors inside emptiness checks are ignored. Direct tests are absent.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/rb-main.go -->
