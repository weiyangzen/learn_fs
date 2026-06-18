# sources/test-tools/syzkaller/pkg/fuzzer/cover.go

## Purpose
`Cover` tracks the maximum fuzzing signal known to a fuzzer and exposes deltas for synchronization. It distinguishes all observed max signal, including flaky observations, from newly observed signal that has not yet been grabbed.

## Important APIs, Types, And Functions
`Cover` holds a mutex, `maxSignal`, and `newSignal`. `newCover` registers a `stat` metric named `max signal`. `addRawMaxSignal` diffs raw signal against the current max with a priority, merges non-empty diffs into both max and new-signal state, and returns the diff. `CopyMaxSignal` returns a thread-safe copy. `GrabSignalDelta` returns accumulated new signal and clears the delta.

## Control Flow
All mutations take the write lock. `addRawMaxSignal` exits early if no new signal exists; otherwise it updates both long-lived and delta state. Readers take the read lock for copy and write lock for consuming deltas.

## State And Persistence Behavior
State is in-memory only. `maxSignal` is cumulative for the process lifetime, while `newSignal` is transient and is reset after `GrabSignalDelta`. The code intentionally treats flaky signal as max signal to suppress repeated triage on already observed bits.

## Dependencies And Integration Points
It depends on `pkg/signal` and `pkg/stat`. `Fuzzer.triageProgCall` and `triageJob.deflake` feed raw executor signals into it. Signal deltas are candidates for propagation to other components.

## Risks
Signal priority is supplied by callers, so wrong priority calculation changes corpus ranking. `GrabSignalDelta` returns the internal map value then nils the field; callers should treat it as owned output and not expect the fuzzer to retain that specific map.

## Test Signals
No direct test file targets `Cover`. It is exercised through fuzzer tests and deflake behavior that add and compare signal.
