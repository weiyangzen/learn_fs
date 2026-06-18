# sources/sync-backup/kopia/repo/maintenancestats/typeconversion_test.go

Purpose: tests signed-to-unsigned stats conversion behavior.

Important APIs/types/functions: `TestToUint64` and `ToUint64`.

Control flow: table cases pass `math.MinInt`, `-1`, `0`, `1`, and `math.MaxInt`, then assert negative inputs become zero and non-negative inputs preserve value.

State/persistence behavior: no state; protects values that later become persisted maintenance stats.

Dependencies/integration: uses `testify/require` and `math` constants.

Risks/test signals: does not assert warning throttling, only conversion results.
