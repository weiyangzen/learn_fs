<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_set.go -->
# sources/sync-backup/kopia/cli/throttle_set.go

## Purpose
Provides shared CLI parsing and application of throttle-setting flags into `throttling.Limits`.

## Important APIs, Types, And Functions
Defines `commonThrottleSet`, `setup`, `apply`, `setThrottleFloat64`, and `setThrottleInt`. It supports download/upload bytes per second, read/write/list request rates, and concurrent reads/writes.

## Control Flow
`apply` calls typed setters for each nonempty flag. A value of `unlimited` or `-` sets the target field to zero; otherwise floats or ints are parsed and assigned. Each assignment increments a caller-provided change count and logs the change.

## State And Persistence Behavior
It mutates only the supplied `throttling.Limits` struct. Persistence depends on the caller, such as `command_server_throttle_set.go`, sending the changed limits to a server.

## Dependencies And Integration Points
Integrates Kingpin flag registration, units formatting for byte speeds, logging, and throttling structs.

## Risks And Edge Cases
No local validation prevents negative speeds/rates/concurrency. The log phrase `to a unlimited` is grammatically odd but harmless. Change count increments even if the new value equals the old value.

## Test Signals
Tests should cover parse failures, unlimited aliases, negative values if allowed/rejected by callers, and change-count behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_set.go -->
