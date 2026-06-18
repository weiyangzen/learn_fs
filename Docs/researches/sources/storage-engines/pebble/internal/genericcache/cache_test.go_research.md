# sources/storage-engines/pebble/internal/genericcache/cache_test.go

## Purpose
`cache_test.go` exercises the generic cache API, CLOCK-Pro policy compatibility, eviction semantics, error handling, and cancellation behavior.

## Important APIs, Types, And Functions
`intKey` implements `Key` with randomized shard distribution for small keys. `TestBasic` validates repeated lookups and miss counts. `TestClockPro` reuses block-cache testdata to compare hit/miss behavior. `TestEvict` verifies explicit eviction and release lists. `TestEvictPanic` confirms outstanding references panic. `TestErrorHandling` tests failed initialization retry. `TestContextCancellation` checks waiting callers can cancel while another goroutine initializes.

## Control Flow
Tests construct caches with simple init/release callbacks, call `FindOrCreate`, inspect values, and unref. The clock-pro test scans `../cache/testdata/cache`, comparing actual hit increments to expected `h`/miss markers. Cancellation test blocks the first initializer and issues canceled/deadline contexts for concurrent waiters.

## State And Persistence Behavior
State is in-memory except the shared hit/miss testdata file. Release callbacks mutate values or append to slices so tests can observe cleanup.

## Dependencies And Integration Points
It depends on `context`, `sync`, `atomic`, `rand/v2`, `testutils.CheckErr`, `testify/require`, and the older block cache’s golden access trace.

## Risks And Edge Cases
The random shard count/distribution increases coverage but can make debugging order-sensitive release lists harder, so tests sort expected slices. The clock-pro test requires a single shard and capacity 200 to match existing golden expectations.

## Test Signals
Passing tests signal stable cache hits, retry after failed initialization, synchronous release on explicit eviction, panic-on-leaked-reference enforcement, and correct context cancellation for waiters without poisoning the eventually successful value.
