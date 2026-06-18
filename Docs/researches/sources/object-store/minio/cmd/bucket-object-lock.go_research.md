# Research: sources/object-store/minio/cmd/bucket-object-lock.go

Purpose: implements object lock/retention decision helpers used by delete, put, lifecycle, quota, and replication paths. It reads bucket retention defaults and enforces legal hold, governance, and compliance semantics.

Important APIs and functions: `BucketObjectLockSys.Get` returns bucket retention from `globalBucketMetadataSys.GetObjectLockConfig`, treating not-found as no retention. `enforceRetentionForDeletion` blocks lifecycle/quota deletion when legal hold is on or retention is unexpired. `enforceRetentionBypassForDelete` evaluates delete requests against object legal hold, compliance retention, governance bypass headers, and `policy.BypassGovernanceRetentionAction`. `enforceRetentionBypassForPut` validates retention updates/overwrites with owner and credential context. `checkPutObjectLockAllowed` parses WORM headers, bucket defaults, version-specific existing object state, replica behavior, and permission errors.

Control flow: delete enforcement first handles benign get-object errors such as not found, version not found, or method-not-allowed for delete markers. Legal hold always blocks. Compliance blocks until retain-until is before NTP time. Governance blocks unless retention is expired or bypass header and permission are present. Put enforcement computes remaining days for policy checks, then applies expired, governance, compliance, or new-retention rules. Header validation in `checkPutObjectLockAllowed` rejects lock headers on non-lock buckets, parses legal hold and retention headers when requested, and applies bucket default retention when appropriate.

State and persistence behavior: this file does not persist state itself. It reads parsed object-lock bucket config and object metadata, then returns retention/legal-hold values or errors that control later object writes/deletes.

Dependencies and integration points: integrates auth credentials, object-lock metadata parsing, replication status, NTP time, S3 policy checks, request headers, versioning options via `getOpts`, object info callbacks, and MinIO error types.

Risks: many branches depend on accurate NTP time; failures conservatively lock objects. Governance bypass requires both header and permission, so authorization regressions can block legitimate operations. Replica handling deliberately differs from normal writes and must stay aligned with replication semantics. Passing precomputed permission errors into `checkPutObjectLockAllowed` makes caller correctness important.

Test signals: no direct tests in this subset. Lifecycle and delete tests may indirectly encounter object-lock paths only if metadata is configured, which these tests do not do. Dedicated object-lock tests are needed for compliance/governance/legal-hold matrices.
