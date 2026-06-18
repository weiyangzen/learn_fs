# sources/sync-backup/kopia/snapshot/policy/upload_policy.go

Purpose: defines upload concurrency and large-file parallelization policy.

Important APIs/types/functions: `UploadPolicy`, `UploadPolicyDefinition`, `Merge`, and `ValidateUploadPolicy`. Fields are optional max parallel snapshots, optional max parallel file reads, and optional size threshold for parallel upload.

Control flow: merge fills optional ints/int64s from a source policy and records source provenance. Validation rejects `MaxParallelSnapshots` on path-specific source policies because that limit is only valid globally, per user-host, or per host.

State and persistence: in-memory policy values are serialized by the wider policy subsystem. Defaults are defined in `policy_tree.go` as one parallel snapshot, CPU-based reads when nil, and 2 GiB parallel-upload threshold.

Dependencies and integration points: consumed by uploader scheduling and policy manager validation, with `snapshot.SourceInfo.Path` determining scope legality.

Risks and test signals: validation is narrow and does not bound numeric values here; callers or UI must avoid nonsensical optional values. Generic policy merge tests cover merge/provenance shape.
