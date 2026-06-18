# sources/object-store/minio/cmd/batch-replicate.go

Purpose: Defines the YAML/configuration schema for MinIO batch replication jobs: source/target resources, credentials, filters, notification/retry flags, and remote/local direction detection.

Important APIs/types/functions: `BatchReplicateFilter` carries newer/older duration filters, created-after/before times, tags, and metadata. `BatchJobReplicateFlags` groups filter, notify, and retry. `BatchJobReplicateResourceType` validates supported resource types (`minio`, `s3`) and exposes `isMinio`. `BatchJobReplicateCredentials` stores access key, secret key, session token, `Empty`, and credential validation via MinIO auth helpers. `BatchJobReplicateTarget` and `BatchJobReplicateSource` describe endpoints, buckets, path style, prefix, credentials, and source snowball settings. `BatchJobReplicateV1` is the v1 request with API version, flags, source, target, and a non-serialized minio core client. `RemoteToLocal` determines direction by presence of source credentials.

Control flow: This file is mostly declarative; validation and execution live in `batch-handlers.go`. Path-style helpers accept `on`, `off`, `auto`, or empty. Resource type validation rejects anything outside MinIO/S3. Credential validation rejects invalid access/secret key shape.

State/persistence behavior: Exported fields are serialized by generated msgp code from the replication file generation set; the runtime `clnt` pointer is excluded with `msg:"-"`. Credentials are persisted in job requests until redacted for describe output, so access controls around job definition storage matter.

Dependencies/integration: Used by batch admin submission, replication start/validate/execute logic, `BatchJobRequest.Type`, redaction, notification, and minio-go client construction. Depends on `miniogo.Core`, internal `auth`, shared common types, and `xtime.Duration`.

Risks/test signals: `RemoteToLocal` infers direction from source credentials rather than endpoint alone; validation must keep those fields consistent. Credentials are sensitive and rely on redaction before display. There are no tests in this subset specifically for replication schema validation, path validation, credential validation, or direction detection; behavior is covered only indirectly by compilation/generated serializers elsewhere.
