# sources/object-store/rustfs/crates/rio-v2/tests/minio_generated_fixtures.rs

Purpose: this Rust integration test file validates that locally generated MinIO backend fixtures can be decoded by RustFS file metadata code and that encryption-related object metadata matches expected SSE modes and upload shapes.

Important APIs and control flow: helper structs deserialize `request.json`, `head.json`, and `manifest.json`. `fixture_root()` uses `RUSTFS_MINIO_FIXTURE_ROOT` or defaults to `tests/fixtures/minio-generated`. `find_object_xl_meta` walks copied backend disks to locate object `xl.meta` while ignoring `.minio.sys`. `load_file_info` reads that metadata and calls `rustfs_filemeta::get_file_info` with `include_free_versions=true`. Test helpers derive metadata maps and expected fixture KMS key IDs from request headers or manifest capture data.

Test coverage: six ignored tests correspond to the lab matrix. Singlepart SSE-S3, SSE-KMS, and SSE-C tests verify request/head metadata, one part, actual sizes, content type, sealed-key metadata, KMS key/context metadata, or SSE-C customer-key metadata. Multipart SSE-S3/KMS/C tests verify two parts totaling 8 MiB, encrypted multipart marker, actual-size metadata, KMS context/key behavior, and SSE-C absence of KMS key IDs.

State and persistence: tests are `#[ignore]` because they require generated fixture directories outside normal unit-test state. They read fixture artifacts but do not mutate them.

Dependencies and integration points: depends on `rustfs-filemeta`, `serde_json`, `walkdir`, and the Python lab output format. It bridges object-store compatibility work to real MinIO backend metadata rather than synthetic byte streams.

Risks and test signals: ignored tests are easy to skip in CI unless a dedicated fixture job enables them. Fixture root discovery and panic-heavy helpers favor developer clarity over graceful failures. Assertions focus on metadata decoding, not full encrypted payload decryption. Still, this is a high-value compatibility signal because it checks real `xl.meta` produced by MinIO across encryption modes.
