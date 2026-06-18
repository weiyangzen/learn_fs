# sources/test-tools/syzkaller/pkg/coveragedb/mocks/RowIterator.go

Purpose: generated testify mock for `spannerclient.RowIterator`.

Important APIs/types/functions: `NewRowIterator`, `RowIterator`, `Next`, `Stop`, and typed helper call structs for both methods.

Control flow: `Next` returns a mocked `spannerclient.Row` and error, supporting either static returns or function returns. `Stop` records a call and has helper methods for return/run behavior.

State and persistence: mock expectations only.

Dependencies and integration: used by coverage DB tests to stream fake rows and emit `iterator.Done`. Depends on `spannerclient` and testify mock.

Risks: missing `Stop` expectations can fail tests because production code defers `Stop`. Type assertions panic on wrong mocked return types.

Test signals: enables precise query lifecycle tests, especially ensuring iterators are stopped.
