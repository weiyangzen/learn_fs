# sources/object-store/minio/cmd/batch-job-common-types.go

Purpose: Defines shared YAML/configuration primitives used across MinIO batch jobs: user-facing validation errors, wildcard key/value matching, notification endpoints, retry policy, snowball transfer options, size filters, and human-readable byte parsing.

Important APIs/types/functions: `BatchJobYamlErr` preserves line/column-aware error messages. `BatchJobKV` captures key/value pairs and implements YAML location capture, `Validate`, `Empty`, and wildcard `Match`. `BatchJobNotification` and `BatchJobRetry` capture endpoint/token and retry attempts/delay; retry rejects negative values. `BatchJobSnowball` configures archive-based replication with optional pointer fields and validates batch size plus `SmallerThan`. `BatchJobSizeFilter` stores upper/lower bounds with `InRange` and `Validate`. `BatchJobSize.UnmarshalYAML` parses humanized byte strings.

Control flow: Each YAML-aware type decodes through an alias to avoid recursion and records the YAML node location for later diagnostics. Filters apply inclusive-style checks as implemented: an upper bound rejects `sz > upper`, and a lower bound rejects `sz < lower`. Wildcard matching is case-insensitive on keys and wildcard-based on values.

State/persistence behavior: These structs are embedded in persisted job requests via generated msgp, but their unexported line/column metadata is not serialized. Pointer fields in `BatchJobSnowball` allow `StartBatchJob` to distinguish omitted values and fill defaults before validation.

Dependencies/integration: Used by expiration, replication, key rotation, admin handlers, and generated serializers. Depends on `humanize.ParseBytes`, MinIO wildcard matching, YAML v3, and time durations.

Risks/test signals: `BatchJobSnowball.Validate` dereferences pointer fields and assumes defaults were filled; calling it before defaulting can panic. The error string for non-positive snowball batch appears to say "non positive zero", which is likely typo-prone. Size-bound comments describe strict inequalities, while implementation treats equality as in range for each individual bound and rejects equal lower/upper during validation. Tests cover size range and invalid range validation; msgp tests cover serialization smoke paths.
