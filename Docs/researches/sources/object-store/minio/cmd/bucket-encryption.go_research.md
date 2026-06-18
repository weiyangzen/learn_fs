# sources/object-store/minio/cmd/bucket-encryption.go

This file defines the bucket encryption configuration system wrapper and XML validation helper. It is intentionally small, delegating storage to the global bucket metadata system and parsing to the internal bucket encryption package.

`BucketSSEConfigSys` is an empty struct used as an in-memory system facade. `NewBucketSSEConfigSys` returns a new instance. `(*BucketSSEConfigSys).Get` retrieves a bucket's SSE config through `globalBucketMetadataSys.GetSSEConfig` and returns the parsed `*sse.BucketSSEConfig` plus error.

`validateBucketSSEConfig` calls `sse.ParseBucketSSEConfig` on the provided reader and accepts the config only if it contains exactly one rule. If parsing fails, it returns the parse error; if the rule count is not one, it returns `Unsupported bucket encryption configuration`.

There is no local persistent state. The integration points are `globalBucketMetadataSys`, `internal/bucket/encryption`, and the HTTP handlers in `bucket-encryption-handlers.go`. This function is part of the enforcement boundary for what MinIO supports from AWS S3 bucket encryption XML.

Risks include the one-rule restriction rejecting otherwise valid multi-rule AWS configurations, caller assumptions around nil configs on metadata errors, and semantic validation being delegated to `sse.ParseBucketSSEConfig`. `bucket-encryption_test.go` verifies that single-rule AES256 and aws:kms configs pass validation. It does not cover multi-rule rejection or malformed XML.
