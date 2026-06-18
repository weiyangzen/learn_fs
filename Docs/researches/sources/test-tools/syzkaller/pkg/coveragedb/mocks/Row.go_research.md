# sources/test-tools/syzkaller/pkg/coveragedb/mocks/Row.go

Purpose: generated testify mock for the `spannerclient.Row` interface.

Important APIs/types/functions: `NewRow`, `Row`, `Row_Expecter`, `EXPECT`, `ToStruct`, and `Row_ToStruct_Call`.

Control flow: `ToStruct` delegates to mock expectations and supports callback population through `Run`, which tests use to fill the pointed destination struct.

State and persistence: in-memory mock expectations only.

Dependencies and integration: used by row iterator fixtures in `coveragedb_test.go` to emulate Spanner row decoding. Depends on testify mock.

Risks: `ToStruct` panics when no return is specified. Because `p` is `any`, test callbacks must type-assert the correct struct pointer.

Test signals: supports deterministic DB query tests without real Spanner.
