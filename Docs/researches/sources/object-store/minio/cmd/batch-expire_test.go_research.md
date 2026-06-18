# sources/object-store/minio/cmd/batch-expire_test.go

Purpose: Unit test for YAML parsing of batch expiration job definitions, especially the `prefix` field shape.

Important APIs/types/functions: `TestParseBatchJobExpire` unmarshals two YAML documents into `BatchJobRequest`: one with `expire.prefix` as a string and another with `expire.prefix` as a list. It verifies `job.Expire.Prefix.F()` returns the expected slice using `slices.Equal`.

Control flow: The test builds representative YAML with two rules (`object` and `deleted`), tags, metadata, size filters, purge config comments, notification, and retry. It fails immediately on YAML unmarshal error, then asserts prefix normalization.

State/persistence behavior: Pure parser test; it does not save jobs, validate buckets, delete objects, or use msgp state.

Dependencies/integration: Exercises `gopkg.in/yaml.v3`, `BatchJobRequest`, `BatchJobExpire`, `BatchJobPrefix.UnmarshalYAML`, `xtime.Duration` parsing, and common nested job types.

Risks/test signals: It verifies representative YAML remains accepted and that single/multiple prefixes normalize correctly. It does not call `Validate`, does not inspect parsed rule fields beyond prefixes, and does not cover invalid YAML, future `createdBefore`, negative retry, or deletion behavior.
