# sources/object-store/minio/cmd/batch-job-common-types_gen.go

Purpose: Generated msgp serialization for common batch job configuration types shared by expire, replicate, and handler request persistence.

Important APIs/types/functions: Implements generated methods for `BatchJobKV`, `BatchJobNotification`, `BatchJobRetry`, `BatchJobSize`, `BatchJobSizeFilter`, and `BatchJobSnowball`. Scalar and map fields serialize as expected; `BatchJobSnowball` pointer fields are nil-aware for omitted/defaultable options.

Control flow: Map decoders switch on field names and skip unknown fields. `BatchJobSize` serializes directly as int64. `BatchJobRetry` encodes duration with msgp duration support. `BatchJobSizeFilter` encodes lower/upper `BatchJobSize` fields. `BatchJobSnowball` allocates pointers when non-nil values are decoded.

State/persistence behavior: Defines the binary representation embedded inside `BatchJobRequest` and nested job-specific structs. Unexported YAML line/column fields are absent, so persisted requests keep values but not source diagnostics.

Dependencies/integration: Depends on `tinylib/msgp` and the common source types. Generated methods are invoked by expire, replicate, key-rotate, and request serializers.

Risks/test signals: Regeneration is required after changes to common types. Pointer nil semantics for snowball are important because handler code fills defaults before validation; persisted nils could be unsafe if consumed without defaulting. Generated tests cover zero-value serialization and benchmarks, but non-nil snowball pointers and non-zero sizes/durations are not explicitly asserted.
