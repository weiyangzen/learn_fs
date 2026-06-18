# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_test.rs

Purpose: Dedicated compatibility tests for the bucket metadata MessagePack codec. It focuses on ensuring RustFS can read MinIO-style metadata and legacy Rust/RMP-serde variants.

Important APIs and types: The file uses `BucketMetadata::marshal_msg` and `BucketMetadata::unmarshal`. `TEST_BUCKET_METADATA_HEX` is a large serialized fixture with many populated fields and timestamp values. Tests exercise time encoding, field aliases, bin/array encodings, numeric booleans, and full-field round trips.

Control flow and state: Tests decode fixed hex fixtures into bytes, unmarshal into `BucketMetadata`, and assert names, timestamps, raw config byte prefixes, lock flags, and updated-at fields. The complete round-trip test constructs a metadata instance with policy, lifecycle, versioning, encryption, tagging, quota, object-lock, notification, replication, bucket-target, public-access-block, and ACL bytes, serializes it, then validates the decoded fields.

Dependencies and integration: Uses `faster_hex`, `rmp::encode`, `time::OffsetDateTime`, and S3-compatible config bytes. It validates behavior implemented in `metadata.rs` and `msgp_decode.rs`.

Risks: The huge fixture is opaque and hard to audit manually, but it provides high-value regression coverage. Some tests are timestamp-precision tolerant by comparing Unix seconds, so nanosecond precision is not checked in every path. The file is compiled only under `#[cfg(test)]` via `bucket/mod.rs`.

Test signals: Strong coverage for codec compatibility: ext8 time, legacy compact time arrays, bin-wrapped ext time, legacy field aliases with byte arrays, bin16/array16 values, numeric bools, and full metadata serialization.
