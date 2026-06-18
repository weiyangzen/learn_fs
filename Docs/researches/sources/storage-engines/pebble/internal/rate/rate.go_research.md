# sources/storage-engines/pebble/internal/rate/rate.go

## Purpose
This file wraps `github.com/cockroachdb/tokenbucket` to provide a thread-safe rate limiter for Pebble internal operations. It implements token-bucket waiting, debt, and dynamic rate updates.

## Important APIs, Types, and Functions
`Limiter` stores a token bucket, current rate, burst size, and optional sleep function under a mutex. `NewLimiter(r,b)` initializes a bucket with tokens per second and burst size. `NewLimiterWithCustomTime` also injects `nowFn` and `sleepFn` for deterministic testing. `Wait(n)` loops until `n` tokens can be fulfilled, sleeping for the token bucket's suggested delay. `Remove(n)` subtracts tokens without waiting and can create debt. `Rate()` returns the configured rate. `SetRate(r)` updates the token bucket rate while preserving burst.

## Control Flow and State
All token-bucket operations are protected by the mutex. `Wait` releases the lock before sleeping, then retries. The bucket starts full according to the external tokenbucket implementation. State is entirely in memory and not persisted.

## Dependencies and Integration
The file depends on `sync`, `time`, and CockroachDB's `tokenbucket` package. It is likely used by Pebble components that need internal throttling without exposing tokenbucket details.

## Risks and Edge Cases
`Wait` can sleep forever if the configured rate is zero or too low and the tokenbucket returns non-progressing delays. `SetRate` does not validate negative or zero inputs. `Remove` debt is intentional but can delay future operations substantially. The custom time path depends on caller-provided functions being coherent.

## Test Signals
No direct tests are included in this work item. The custom time constructor is a strong signal that deterministic tests exist or are intended elsewhere.
