# sources/sync-backup/kopia/internal/contentlog/logparam/logparam_test.go

Purpose: verifies typed log parameter constructors and `WriteValueTo` methods produce valid JSON and avoid allocations.

Important APIs/types/functions: tests for `String`, `Int64`, `Int`, `Int32`, `Bool`, `Time`, `Error`, `UInt64`, `Duration`, and `TestWriteValueToMemoryAllocations`.

Control flow: table-driven tests measure `testing.AllocsPerRun` for each constructor, write a one-field JSON object through `JSONWriter`, unmarshal it, and compare expected values. The allocation test reuses one writer while invoking each `WriteValueTo`.

State and persistence behavior: in-memory only. The tests verify param values are immutable enough for repeated writer use.

Dependencies/integration: uses `clock.Now`, `contentlog`, `pkg/errors`, `encoding/json`, and `testify/require`.

Risks/test signals: repeated writes to the same writer in allocation tests do not reset the buffer, so allocation measurement is the main signal rather than JSON validity there. JSON unmarshalling converts large integers to floats, masking precision concerns.
