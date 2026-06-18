# sources/object-store/minio/cmd/metacache-bucket_test.go

## Purpose

`metacache-bucket_test.go` contains a benchmark for `bucketMetacache.findCache`. It is performance-oriented coverage for cache creation/indexing under many cache IDs and repeated base paths.

## Important Benchmark Flow

`Benchmark_bucketMetacache_findCache` creates an empty bucket metacache without cleanup, defines 50,000 elements across 100 path names, preloads the cache by calling `findCache` with a fresh UUID, bucket `""`, a rotating `BaseDir`, slash separator, strict disk asking, and `Create: true`. After reporting allocations, the benchmark loop continues creating new metacache entries with rotating base dirs and fresh IDs.

The benchmark depends on `mustGetUUID`, `listPathOptions`, and the path/root derivation inside `newMetacache`.

## Risks And Test Signals

The benchmark signals expected allocation/performance pressure for large cache maps, but it has no assertions. It does not cover cache hits, `Create: false`, cleanup thresholds, root-index correctness, deletion, or concurrent access. Functional behavior for `bucketMetacache` is therefore mostly covered indirectly by listing tests outside this subset.
