# Research: sources/object-store/minio/cmd/bucket-policy-handlers.go

Purpose: implements S3 bucket policy PUT, GET, and DELETE handlers. Policies are validated, stored in bucket metadata, returned as JSON, and replicated through site-replication hooks.

Important APIs and functions: `maxBucketPolicySize` enforces the S3 20 KiB policy limit. `bucketPolicyConfig` names the metadata slot as `policy.json`. `PutBucketPolicyHandler` authorizes `policy.PutBucketPolicyAction`, checks bucket existence, requires positive Content-Length, rejects oversized policy bodies, parses with `policy.ParseBucketPolicyConfig`, rejects empty policy version, stores canonical JSON through `globalBucketMetadataSys.Update`, and calls `globalSiteReplicationSys.BucketMetaHook`. `DeleteBucketPolicyHandler` authorizes delete, checks bucket existence, deletes metadata through `globalBucketMetadataSys.Delete`, and emits a replication hook. `GetBucketPolicyHandler` authorizes get, checks bucket existence, loads through `globalPolicySys.Get`, marshals JSON, and writes it.

Control flow: all handlers follow context/audit/objectAPI/auth/bucket-exists patterns. PUT reads the exact declared content length using `io.LimitReader`, converts parser errors into `MalformedPolicy` API errors, and persists marshaled policy rather than raw request bytes. DELETE returns no content on success. GET uses policy subsystem rather than metadata system directly.

State and persistence behavior: policy JSON is stored in bucket metadata with an updated-at timestamp. PUT and DELETE notify site replication using the original policy bytes for PUT and timestamp-only metadata for DELETE.

Dependencies and integration points: integrates HTTP request handling, MinIO auth, bucket metadata system, policy parser/evaluator, site replication metadata hooks, mux route vars, and audit logging.

Risks: PUT relies on `ContentLength`; chunked or missing-length policy uploads are rejected. Parser/canonical JSON output can change response ordering. Site replication hook failures are logged with `replLogIf` rather than failing the client after local persistence succeeds.

Test signals: `bucket-policy-handlers_test.go` covers create bucket concurrency, policy PUT validation, oversized/missing body, invalid policy, resource bucket mismatch, missing/invalid buckets, empty version, GET/DELETE behavior, anonymous request denial, V2/V4 signing, and nil object-layer paths. It does not assert replication hook behavior.
