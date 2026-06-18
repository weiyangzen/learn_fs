# sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs

## sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs

Purpose: e2e tests for Snowball auto-extract behavior during S3 `PutObject` tar uploads. The suite validates MinIO-compatible metadata headers, standard `x-amz-meta-*` headers, prefix normalization, directory marker handling, invalid-entry tolerance, path traversal rejection, and header precedence.

Important APIs and functions: `build_test_archive` creates an in-memory tar with directories, an empty directory, a nested file, and a root file. `build_archive_with_invalid_entry` appends a valid file followed by an entry with an overlong name. `build_archive_with_parent_dir_entry` manually constructs a tar record for `../{victim_bucket}/evil-injected.txt` to test traversal protection. Tests use `RustFSTestEnvironment`, AWS SDK S3 `ByteStream`, `tokio_tar`, and `ProvideErrorMetadata` for error-code assertions.

Control flow: each serial test starts a temporary RustFS server, creates buckets, uploads tar data with extraction metadata, then uses `GetObject`, `HeadObject`, or `ListObjectsV2` to verify extracted results. Prefix tests confirm `/tenant-a/`, `tenant-b`, and standard `/tenant-standard/` prefixes normalize into object keys. Directory tests assert markers are created by default but skipped when ignore-dirs is true. Invalid-entry tests assert valid files extract while invalid entries are ignored when ignore-errors is true. The traversal test expects `InvalidArgument` and confirms the victim bucket has no injected object. Header precedence verifies exact `x-amz-meta-minio-snowball-prefix` wins over a suffix-matching fallback header.

State and persistence: state is isolated to per-test temporary RustFS servers and buckets. Auto-extraction mutates object storage by creating objects from tar entries; directory markers are zero-length objects unless ignored. Tests explicitly stop the server at the end.

Dependencies and integration points: test harness common utilities, AWS SDK S3, tar archive parsing path, Snowball metadata option parsing, object namespace safety checks, list/head/get APIs, and serial execution.

Risks: tests rely on actual server process startup and tar parsing behavior. Some invalid archive construction depends on tar header details. Manual traversal archive crafting is valuable but narrow: it tests parent directory traversal across buckets, not every path normalization edge. Error-code assertions expect `InvalidArgument` or `NotFound` exactly.

Test signals: strong e2e signal for auto-extract compatibility, safety, option parsing, prefix precedence, and partial extraction behavior under ignored errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs -->
