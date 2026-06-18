# sources/object-store/minio/cmd/batch-job-common-types_test.go

Purpose: Handwritten semantic tests for batch job size filtering and validation.

Important APIs/types/functions: `TestBatchJobSizeInRange` validates `BatchJobSizeFilter.InRange` for an object inside a lower/upper range, below lower, above upper, only upper, and only lower. `TestBatchJobSizeValidate` verifies unspecified, lower-only, and upper-only filters are valid, while lower greater than or equal to upper returns `BatchJobYamlErr` with message `invalid batch-job size filter`.

Control flow: Table-driven subtests call the target method and compare booleans or error messages. Error comparison intentionally uses `BatchJobYamlErr.message()` to ignore YAML line/column fields.

State/persistence behavior: Pure unit tests; they do not parse YAML, persist jobs, or interact with object storage.

Dependencies/integration: Exercises `BatchJobSizeFilter`, `BatchJobSize`, `BatchJobYamlErr`, and Go `testing`.

Risks/test signals: Good focused coverage for size range behavior, including invalid empty ranges. It does not test exact equality at single bounds, humanized byte YAML parsing, or integration with expiration rule matching.
