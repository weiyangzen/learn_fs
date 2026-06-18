# sources/test-tools/syzkaller/pkg/cover/manager_to_ci_test.go

Purpose: validates JSONL serialization of manager coverage plus CI details.

Important APIs/types/functions: `sampleCoverJSON` and `TestWriteCIJSONLine`.

Control flow: the test unmarshals a sample `CoverageInfo`, writes a combined record into a buffer with `WriteCIJSONLine`, and compares against an exact compact JSON string with trailing newline.

State and persistence: in-memory buffer only.

Dependencies and integration: uses `encoding/json`, testify assertions, `CoverageInfo`, `CIDetails`, and `WriteCIJSONLine`.

Risks: exact string comparison makes field-order changes visible, which is useful for BigQuery schema compatibility but can be brittle if struct field order is intentionally changed.

Test signals: strong guard that manager-to-CI output remains aligned with the expected ingestion shape.
