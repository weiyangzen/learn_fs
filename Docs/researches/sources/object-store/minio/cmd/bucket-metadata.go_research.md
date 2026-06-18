# Research: sources/object-store/minio/cmd/bucket-metadata.go

Purpose: defines the persisted `BucketMetadata` record, metadata file format, migration from legacy per-config files, parsing of raw config bytes into typed private fields, serialization to `.metadata.bin`, and optional KMS encryption/decryption for bucket target metadata.

Important APIs and types: constants include `bucketMetadataFile`, `bucketMetadataFormat`, and `bucketMetadataVersion`. `BucketMetadata` stores bucket name, creation time, raw XML/JSON config bytes, per-config updated timestamps, and unexported parsed configs. Key methods/functions are `newBucketMetadata`, `lastUpdate`, `Versioning`, `ObjectLocking`, `SetCreatedAt`, `readBucketMetadata`, `loadBucketMetadataParse`, `loadBucketMetadata`, `parseAllConfigs`, `getAllLegacyConfigs`, `convertLegacyConfigs`, `defaultTimestamps`, `Save`, `migrateTargetConfig`, `encryptBucketMetadata`, and `decryptBucketMetadata`.

Control flow: loading reads `.minio.sys/buckets/<bucket>/.metadata.bin`, validates a four-byte little-endian format/version header, and msgp-unmarshals the payload. If metadata is absent or has zero creation time, legacy config files are discovered and converted into raw fields, saved as metadata, and legacy files are deleted best-effort. `parseAllConfigs` builds typed policy, notification, lifecycle, SSE, tagging, object lock, versioning, quota, replication, and target configs from raw bytes. `Save` re-parses first, writes the binary header, appends msgp data, and calls `saveConfig`.

State and persistence behavior: `.metadata.bin` is the main persisted state for bucket settings. Legacy object-lock enabled state is migrated to current object-lock and versioning XML. Updated timestamps default to `Created` if missing. Bucket target config may be encrypted with KMS and SIO, with crypto metadata stored separately in the metadata record.

Dependencies and integration points: integrates MinIO policy, event notification, lifecycle, object lock, versioning, encryption, tagging, quota, replication, bucket targets, object-layer config helpers, KMS, and msgp generated methods in `bucket-metadata_gen.go`.

Risks: adding or removing fields requires regenerating msgp code and considering format/version semantics. `parseAllConfigs` returns on first error, so one malformed config can prevent loading other metadata. Legacy migration deletes old files after saving; partial failures can leave mixed state. Encryption depends on `GlobalKMS` and associated-data consistency.

Test signals: generated msgp tests verify empty `BucketMetadata` serialization behavior. Handler tests indirectly verify policy/lifecycle persistence. There is no direct test here for legacy migration, parse failure handling, encryption/decryption, timestamp defaulting, or object-lock/versioning migration.
