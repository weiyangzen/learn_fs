# sources/storage-engines/pebble/sstable/blob/fetcher.go

## Purpose
This file implements `ValueFetcher`, the hot-path component that retrieves separated values from blob files using blob handles, reader caching, index blocks, and value block caching.

## Important APIs, Types, and Functions
`ValueReader` abstracts blob file readers that can return index and value blocks and initialize read handles.

`ReaderProvider` obtains `ValueReader`s for object metadata, typically through Pebble's file cache.

`SuggestedCachedReaders` sizes the fetcher's reader cache from read amplification.

`ValueFetcher.Init`, `FetchHandle`, `Fetch`, `retrieve`, and `Close` provide the public lifecycle and retrieval APIs implementing `base.ValueFetcher`.

`cachedReader` stores a value reader, close function, read handle, lazy-loaded index block decoder, and currently loaded value block decoder.

`cachedReader.GetUnsafeValue` remaps virtual block IDs when needed, reads the relevant physical block, records retrieval profiling, and returns a slice into cached block data.

## Control Flow
On first retrieval, `ValueFetcher` obtains a pooled cached-reader set sized to `maxCachedReaders` with a minimum allocation. Each lookup scans the reader array for the blob file ID or the least recently used slot. Cache misses close any replaced reader, map the blob file ID to object info, obtain a new reader, initialize a read handle, and update stats.

Within a cached reader, the index block is read lazily. If the requested virtual block differs from the loaded block, it remaps through the index block if rewritten, loads the physical value block, and releases the previous block. It then converts the handle's value ID plus any value-ID offset into a raw-bytes index and returns that value.

## State and Persistence Behavior
No persistent state is written. Runtime state includes cached file readers, read handles, block buffer handles, decoded metadata pointers, fetch counts, stats, and optional invariant buffer mangling. Returned values are unsafe slices valid only until the next fetch on that reader or close.

## Dependencies and Integration Points
The fetcher integrates with base blob file mapping and value fetcher interfaces, objstorage read handles, block cache/read environments/stats, file cache reader providers, blob `HandleSuffix`, index/value block decoders, and value retrieval profiling.

## Risks
This is a performance-sensitive path with O(cache-size) reader lookup. It relies on callers closing the fetcher to release readers and block buffers. Returned values are not caller-owned. Virtual remapping and unreferenced sentinel handling must match rewrite encoding. Bounds checks are invariant-based, so corrupted files must be caught earlier by block/index initialization where possible.

## Test Signals
`fetcher_test.go` covers datadriven fetcher cache state, multi-file reader reuse, randomized sequential and random retrieval over large blobs, and benchmarks for cached/uncached retrieval patterns.
