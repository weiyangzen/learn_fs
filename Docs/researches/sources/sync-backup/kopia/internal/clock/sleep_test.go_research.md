# sources/sync-backup/kopia/internal/clock/sleep_test.go

Purpose: validates that `SleepInterruptibly` exits early on context cancellation and returns true after a complete sleep.

Important APIs/types/functions: `TestSleepInterruptibly_ContextCanceled`, `TestSleepInterruptibly_ContextNotCanceled`, `context.WithTimeout`, and `timetrack.StartTimer`.

Control flow: the cancellation test sets a 100 ms timeout against a 3 second sleep and expects `false` plus elapsed time between 90 ms and 1 second. The non-canceled test sleeps 100 ms on `context.Background()` and expects `true` within the same broad duration bounds.

State and persistence behavior: no persistent state. Tests measure elapsed real time.

Dependencies/integration: uses `testify/require`, `timetrack`, `context`, and `time`.

Risks/test signals: wall-clock assertions may be flaky on overloaded systems, though the 1 second upper bound is generous. The tests do not cover already-canceled contexts or zero/negative durations.
