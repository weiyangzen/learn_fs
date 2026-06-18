# sources/object-store/rustfs/crates/ecstore/src/bucket/migration.rs

Purpose: Migrates legacy meta-bucket artifacts into the RustFS meta bucket. It handles bucket metadata, replication resync metadata, and IAM config normalization from older JSON/time field shapes into RustFS-compatible forms.

Important APIs and types: `try_migrate_bucket_metadata` lists buckets and copies `.metadata.bin` plus `.replication/resync.bin` from `MIGRATING_META_BUCKET` to `RUSTFS_META_BUCKET` when missing. `try_migrate_iam_config` paginates under `config/iam/`, normalizes supported IAM objects, and writes missing targets. Internal helpers include `normalize_iam_config_blob`, path classifiers for identity/group/policy/mapping files, `normalize_bucket_meta_blob`, and `migrate_one_if_missing`.

Control flow and state: Migration is idempotent: an existing target object causes a skip. Unsupported paths are skipped, incompatible data logs a warning and is not written, and empty reads are ignored. IAM normalization fills missing versions/update timestamps, converts legacy policy mapping field aliases, and preserves policy document create/update dates. Resync metadata is decoded and re-encoded through replication helpers.

Dependencies and integration: Relies on generic store traits (`BucketOperations`, `ListOperations`, `ObjectIO`, `ObjectOperations`), meta bucket constants, `PutObjReader`, IAM policy/user types, HTTP headers, and replication resync encode/decode.

Risks: Migration silently skips on listing/read failures, which is safe for startup but can hide incomplete migration unless logs are monitored. Existing target objects are never overwritten, so corrupted partial target state will not self-heal. Bucket migration uses disk bucket listing rather than listing legacy meta objects, which assumes all relevant buckets are visible through `list_bucket`.

Test signals: Unit tests cover legacy policy mapping timestamp/field normalization and resync metadata re-encoding. There are no tests with a fake store for pagination, idempotent copy, or read/write failure paths.
