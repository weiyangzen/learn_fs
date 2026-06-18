# sources/object-store/minio/cmd/bucket-encryption_test.go

This test file covers `validateBucketSSEConfig`, the parser/validator used by bucket encryption HTTP handlers. `TestValidateBucketSSEConfig` defines XML fixtures and verifies whether validation succeeds.

The first fixture is a single-rule SSE-S3 configuration with `SSEAlgorithm>AES256</SSEAlgorithm>`. The second fixture is a single-rule SSE-KMS configuration with `SSEAlgorithm>aws:kms</SSEAlgorithm>` and `KMSMasterKeyID>my-key</KMSMasterKeyID>`. Both are expected to pass. For failing cases, the test would compare the returned error string to `expectedErr`, but the current table contains no failing entries.

The test has no persistent state and depends only on `bytes`, `testing`, and `validateBucketSSEConfig`. It is a narrow parser-validation signal confirming MinIO accepts the two common single-rule encryption modes.

Coverage gaps are notable: no multi-rule unsupported config, malformed XML, empty config, unsupported algorithms, missing KMS key ID semantics, size limits, HTTP authorization, KMS probing, metadata persistence, or site-replication behavior. Because both fixtures pass, the negative branch in the test is currently unexercised.
