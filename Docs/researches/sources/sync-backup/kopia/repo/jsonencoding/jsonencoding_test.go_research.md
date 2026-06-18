# sources/sync-backup/kopia/repo/jsonencoding/jsonencoding_test.go

Purpose: tests JSON marshaling and unmarshaling behavior for `jsonencoding.Duration`.

Important APIs/types/functions: `MyStruct`, `TestDurationJSONMarshaling`, `TestDurationJSONUnmarshaling`, and `TestDurationJSONUnmarshalingError`.

Control flow: one test marshals a 20m10s duration and asserts JSON text. The table-driven unmarshal test parses duration strings, whitespace-padded values, and numeric nanoseconds. The error test verifies invalid strings report "invalid duration".

State/persistence behavior: no external state; it protects config compatibility for duration fields.

Dependencies/integration: uses `encoding/json`, `time`, and `testify/require`.

Risks/test signals: catches regressions in numeric legacy parsing and error propagation. It does not test fractional numeric strings or direct non-JSON text calls.
