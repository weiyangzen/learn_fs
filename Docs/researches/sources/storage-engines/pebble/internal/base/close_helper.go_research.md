<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/close_helper.go -->
# sources/storage-engines/pebble/internal/base/close_helper.go

## Purpose
This file provides an idempotent wrapper around `io.Closer`.

## Important APIs, Types, And Functions
`CloseHelper` returns a `closeHelper` containing the original closer. `closeHelper.Close` closes once, nils the stored closer, and returns nil on later calls.

## Control Flow
`Close` snapshots the closer, returns nil if already nil, otherwise clears the field before invoking the underlying `Close`.

## State And Persistence Behavior
State is only the wrapper's pointer to the closer. It prevents duplicate close side effects in error/defer paths.

## Dependencies And Integration Points
It depends only on `io`. It can wrap files, readers, writers, or cleanup resources throughout Pebble.

## Risks And Edge Cases
The helper is not synchronized; concurrent `Close` calls on the same wrapper can race. It is intended for single-goroutine cleanup paths.

## Test Signals
No direct test in this subset; behavior is simple and likely exercised indirectly by callers that rely on idempotent cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/close_helper.go -->
