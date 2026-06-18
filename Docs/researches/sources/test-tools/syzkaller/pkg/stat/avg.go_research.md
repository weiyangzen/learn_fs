# sources/test-tools/syzkaller/pkg/stat/avg.go

## Purpose

`avg.go` provides a thread-safe incremental average helper currently constrained to `time.Duration`-like values.

## Important APIs, Types, And Control Flow

`AverageParameter` is a type constraint over `time.Duration`. `AverageValue[T]` stores a mutex, sample count, and current average. `Save` increments the sample count and applies the incremental formula `avg += (val - avg) / total`; `Value` returns the current average under lock.

## State, Dependencies, Integration, Risks, And Test Signals

State is in-memory and protected by `sync.Mutex`. It depends only on `time` and `sync`. The integer-duration formula is stable and O(1), but truncates fractional parts and `total` could overflow after extreme runtimes. There are no tests in this subset; callers should test first sample behavior, multiple samples, and concurrent `Save`/`Value`.
