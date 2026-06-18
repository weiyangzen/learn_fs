# sources/object-store/minio/cmd/bucket-encryption-handlers.go

This file implements S3 bucket encryption configuration handlers: put, get, and delete. It stores encryption XML in bucket metadata, validates KMS availability and key usability, and invokes site-replication metadata hooks.

`bucketSSEConfig` names the metadata object `bucket-encryption.xml`. `PutBucketEncryptionHandler` builds request context/audit logging, checks object layer initialization, extracts the bucket, authorizes `policy.PutBucketEncryptionAction`, verifies bucket existence, parses and validates XML with `validateBucketSSEConfig` under `maxBucketSSEConfigSize`, requires `GlobalKMS`, and if a KMS key ID is configured probes it with `GlobalKMS.GenerateKey`. KES key-not-found is translated to `errKMSKeyNotFound`; other KMS failures are returned as API errors. The validated config is marshaled to XML and written through `globalBucketMetadataSys.Update`. The site-replication hook receives base64 XML in `madmin.SRBucketMeta` with type `SSEConfig`, then the handler returns headers-only success.

`GetBucketEncryptionHandler` authorizes `policy.GetBucketEncryptionAction`, checks bucket existence, retrieves the config from `globalBucketMetadataSys.GetSSEConfig`, marshals it, and writes XML. `DeleteBucketEncryptionHandler` authorizes via put-encryption permission, checks bucket existence, deletes the metadata entry, sends a site-replication hook with nil config, and returns 204.

Persistent state is bucket metadata plus site-replicated metadata timestamps. Dependencies include S3 policy auth, bucket metadata subsystem, KMS/KES, XML/base64 encoding, madmin site replication structs, and audit/error response helpers.

Risks include KMS being mandatory even for delete/put paths where behavior may surprise users, correctness of base64 metadata replication, XML size/parse handling, and mapping KMS failures to S3-compatible errors. `bucket-encryption_test.go` covers validation of single-rule SSE-S3 and SSE-KMS XML but not HTTP handlers, KMS failure paths, persistence, or replication hooks.
