<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options_test.go -->
# sources/storage-engines/badger/options_test.go

## Purpose
This file tests option superflag serialization and parsing.

## Important APIs, Types, And Functions
`TestOptions` has default round-trip and special-flag subtests. `optionsEqual` reflectively compares exported scalar option fields for bool, int/int64, uint32/uint64, float64, and string kinds.

## Control Flow
The default test serializes `DefaultOptions("")` with `generateSuperFlag`, parses into an empty `Options`, and checks equality with defaults. It also verifies a simple override of `numgoroutines`. The special-flags test configures namespace offset, ZSTD compression, compression level, and goroutine count, then parses the equivalent superflag and compares.

## State And Persistence Behavior
There is no DB persistence. The tests validate configuration state translation before DB open.

## Dependencies And Integration Points
The test depends on `reflect`, `testing`, and the `options` enum package. It covers `options.go` helper functions rather than runtime DB behavior.

## Risks And Edge Cases
`optionsEqual` ignores non-scalar/exported unsupported fields such as logger and byte slices, matching superflag limitations. Invalid compression strings, numeric compression fallback, and panic paths are not covered.

## Test Signals
Signals are equality after default superflag round-trip and correct parsing of `compression=zstd:2`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options_test.go -->
