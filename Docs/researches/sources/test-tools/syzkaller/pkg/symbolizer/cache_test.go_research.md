# sources/test-tools/syzkaller/pkg/symbolizer/cache_test.go

## Purpose

This file tests that `Cache.Symbolize` memoizes both successful symbolization results and errors by binary plus PC.

## Important APIs, Types, And Functions

`TestCache` defines an `inner` function that tracks calls in a `map[cacheKey]bool`, returns frames for normal bins, and returns formatted errors for bin `"error"`. A local `check` helper compares cached results.

## Control Flow, State, Dependencies, And Integration

The test invokes repeated lookups for identical and different keys. It asserts the inner function is not called twice for the same `(bin, pc)` pair. Assertions use testify equality on frame slices and errors.

## Risks And Test Signals

This catches basic cache-key mistakes and confirms negative caching. It does not exercise concurrency, mutation of returned frames, or multi-PC inner calls beyond the one-PC production cache API.
