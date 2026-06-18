# sources/test-tools/syzkaller/pkg/coveragedb/mocks/SpannerClient.go

Purpose: generated testify mock for the `spannerclient.SpannerClient` interface.

Important APIs/types/functions: `NewSpannerClient`, `SpannerClient`, `Apply`, `Close`, `Single`, and typed helper call structs.

Control flow: `Apply` handles variadic `spanner.ApplyOption` by including options in `mock.Called` only when present, then returns a commit timestamp and error. `Single` returns a mocked read-only transaction. `Close` records a call.

State and persistence: in-memory expectations only.

Dependencies and integration: used by `coveragedb_mock_test.go`, `coveragedb_test.go`, and `covermerger_test.go` to validate persistence and query flows without real Spanner.

Risks: variadic option handling must match expectation setup. Return type mistakes panic. Generated code should remain in sync with the interface.

Test signals: core test infrastructure for Spanner mutation count assertions and query fixture assembly.
