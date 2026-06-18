# sources/test-tools/syzkaller/pkg/testutil/testutil.go

## Purpose

`testutil.go` contains shared test helpers for iteration scaling, deterministic randomness, random value construction, and test-log-backed writers.

## Important APIs, Types, And Functions

`IterCount` returns 1000, reduced in short or race builds. `RandSource` chooses a seed from current time, `SYZ_SEED`, or `0` in CI, and logs it. `RandMountImage` returns up to 1 MiB of random bytes. `RandValue` and `randValue` recursively generate values with special handling for slices, arrays, structs, pointers, maps, and `time.Time`. `Writer.Write` logs bytes through `testing.TB`.

## Control Flow, State, Dependencies, And Integration

Randomness is caller-local except for environment variables. Reflection recurses through type shapes and calls `testing/quick.Value` for primitive/default cases. Integration points are fuzz-like tests and helpers that need reproducible seeds.

## Risks And Test Signals

`randValue` uses package-level `rand.Intn` in some branches instead of the supplied `rnd`, weakening seed determinism for sizes and pointer/map choices. It can panic/fail on unexported struct fields or unsupported quick types. There are no direct tests in this subset; usage across tests is the signal.
