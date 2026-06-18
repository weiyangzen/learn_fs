# sources/sync-backup/kopia/internal/clock/sleep.go

Purpose: provides an interruptible sleep helper that returns whether the requested duration completed.

Important APIs/types/functions: `SleepInterruptibly(ctx context.Context, dur time.Duration) bool`.

Control flow: performs a `select` between `ctx.Done()` and `time.After(dur)`. It returns `false` when the context is canceled first and `true` when the timer fires first.

State and persistence behavior: no state or persistence. The `time.After` timer is allocated for each call and not stopped explicitly, which is acceptable for simple one-shot sleep use.

Dependencies/integration: used anywhere long waits should honor cancellation.

Risks/test signals: for very high-frequency use, repeated `time.After` can allocate. Tests assert both cancellation-before-duration and full-duration completion with broad timing bounds.
