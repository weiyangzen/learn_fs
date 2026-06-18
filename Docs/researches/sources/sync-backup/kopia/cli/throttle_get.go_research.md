<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_get.go -->
# sources/sync-backup/kopia/cli/throttle_get.go

## Purpose
Provides shared formatting for throttling limits used by server throttle and storage/provider-related commands.

## Important APIs, Types, And Functions
Defines `commonThrottleGet`, `setup`, `output`, `printValueOrUnlimited`, and `floatToString`. It prints `throttling.Limits` as JSON or aligned text.

## Control Flow
Commands call `setup` to register JSON flags and output services, then `output` prints download/upload speeds, request rates, and concurrency limits. Zero values are displayed as `(unlimited)`.

## State And Persistence Behavior
No persistent state is changed. It only formats a provided limits struct.

## Dependencies And Integration Points
Depends on `json_output.go`, text output services, `internal/units`, and `repo/blob/throttling`.

## Risks And Edge Cases
Integer concurrency limits are converted through float64 for common formatting, which is fine for practical values but unnecessary. Text labels are part of CLI compatibility.

## Test Signals
Tests should cover JSON mode, unlimited zeros, finite speeds/rates/concurrency, and formatting stability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_get.go -->
