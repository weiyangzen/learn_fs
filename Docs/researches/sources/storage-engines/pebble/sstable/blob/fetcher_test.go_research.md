# sources/storage-engines/pebble/sstable/blob/fetcher_test.go

## Purpose
This file tests and benchmarks blob `ValueFetcher` retrieval, reader caching, block caching, and sequential/random access patterns.

## Important APIs, Types, and Functions
`identityFileMapping` maps blob file IDs directly to disk file numbers for tests.

`mockReaderProvider` records reader requests and returns prebuilt `FileReader`s.

`TestValueFetcher` is a datadriven harness with `define`, `new-fetcher`, and `fetch` commands.

`writeValueFetcherState` prints cached reader slots and current physical block indexes.

`TestValueFetcherRetrieveRandomized` writes about 4 MiB of random values and validates sequential and random retrieval against saved handles.

`BenchmarkValueFetcherRetrieve` and `benchmarkValueFetcherRetrieve` measure sequential/random retrieval with and without block cache priming.

`makeMockReaderProvider` constructs readers with optional block cache handles and can prepopulate value blocks.

## Control Flow
Datadriven `define` writes a blob file into a memory object, opens a `FileReader`, and registers it. `new-fetcher` creates a fetcher with a selected reader cache size. `fetch` encodes a handle suffix, calls `FetchHandle`, prints cache state, and prints the returned value.

Randomized tests generate values and handles, close the writer, open a reader, then exercise `retrieve` in sequential and shuffled orders. Benchmarks generate larger blob files and repeatedly fetch handles.

## State and Persistence Behavior
Memory objects hold blob files for each test. Fetchers and readers are closed in defers. Optional cache state is held by `cache.Cache` and `cache.Handle`.

## Dependencies and Integration Points
Tests integrate with objstorage memory objects, block reader cache options, sstable internal cache options, random test utilities, and leaktest.

## Risks
Randomized tests log time-based seeds, so failures require seed capture. Benchmarks are sensitive to compression/block-cache behavior and hardware. The mock provider's close function is a no-op, so production file-cache refcount behavior is not fully modeled.

## Test Signals
Signals include exact returned values, expected reader cache state, reader cache miss traces, equality over randomized retrieval, and benchmark performance deltas for cached versus uncached access.
