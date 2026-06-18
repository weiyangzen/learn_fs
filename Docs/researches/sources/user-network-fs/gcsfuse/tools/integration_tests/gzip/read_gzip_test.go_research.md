# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/read_gzip_test.go

Purpose: verifies full-file and ranged reads of gzip-related GCS objects through gcsfuse preserve compressed bytes and object size semantics across content-encoding/no-transform variants.
Important APIs/functions: `verifyFileSizeAndFullFileRead`, `verifyRangedRead`, `downloadGzipGcsObjectAsCompressed`, and ten exported tests covering text/gzip content with/without content encoding and no-transform.
Control flow: full-read tests stat the mounted file, compare mounted size to GCS object size, download the same object using `ReadCompressed(true)`, and compare bytes. Ranged tests compute offsets/sizes, read chunks from mounted and downloaded compressed files, and compare buffers.
State and persistence: reads fixture objects under `gzip/` created by `gzip_test.go`; creates local temp compressed downloads for comparison and removes them.
Dependencies and integration points: uses Cloud Storage client `ReadCompressed(true)` because gcloud/gsutil decompress content-encoded gzip by default. Depends on operations read/stat/compare helpers.
Risks and edge cases: ranged read uses several fixed offset multipliers and assumes object size supports them. It opens a file handle `f` in `verifyRangedRead` but does not use/close it, which can leak descriptors in long runs.
Test signals: mounted bytes and sizes must exactly match compressed GCS object bytes for full and ranged reads.
