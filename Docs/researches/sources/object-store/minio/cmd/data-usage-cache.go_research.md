# sources/object-store/minio/cmd/data-usage-cache.go

## Purpose
`data-usage-cache.go` defines MinIO's data-usage cache tree, serialized cache versions, bucket/tier usage aggregation, compaction/merge helpers, hash-based scan scheduling, and object-store load/save behavior for scanner results.

## Important APIs, Types, And Functions
Core types include `dataUsageHash`, `sizeHistogram`, `versionsHistogram`, `dataUsageEntry`, `allTierStats`, `tierStats`, `dataUsageCache`, legacy cache versions V2-V7, `dataUsageCacheInfo`, `dataUsageHashMap`, and `currentScannerCycle`. Entry/cache helpers include `addSizes`, `merge`, `mod`, `modAlt`, `addChild`, `clone`, `find`, `isCompacted`, `findChildrenCopy`, `searchParent`, `deleteRecursive`, `dui`, `replace`, `replaceHashed`, `copyWithChildren`, `reduceChildrenOf`, `forceCompact`, `flatten`, histogram conversion, `tiersUsageInfo`, `bucketsUsageInfo`, `sizeRecursive`, `merge`, `load`, `save`, `serializeTo`, `deserialize`, and `hashPath`.

## Control Flow
Scanner code builds/updates a tree keyed by cleaned path hashes. Recursive helpers copy or flatten children, compact least-useful subtrees when limits are exceeded, remove unreachable entries, merge per-drive roots, and convert flattened data into `DataUsageInfo`. Load first tries bucket metadata cache, falls back to the older `dataUsageBucket`, retries primary/backup objects, and ignores missing caches. Save serializes to zstd-compressed msgp with a version byte, writes the primary object, and best-effort writes a backup.

## State And Persistence Behavior
Caches are persisted as versioned compressed objects under `.minio.sys/buckets/...` via `saveConfig`; backups use `name + ".bkp"`. Saves are concurrency-limited to four. Deserialization migrates V2-V7 schemas to current version 8, including histogram conversion from V1 intervals.

## Dependencies And Integration Points
It integrates with scanner folder compaction, data usage admin reports, object-layer config I/O, msgp code generation, zstd compression, xxhash scheduling, bytebuffer pooling, bucket/tier metadata, lifecycle config references in cache info, and current scanner cycle metrics.

## Risks And Test Signals
Risks include cache corruption from lockless reads/writes, best-effort backup save errors being deferred/ignored, path-hash/key assumptions, expensive recursive flattening on huge trees, and migration gaps when cache versions change. There are no direct tests in this subset; behavior is indirectly exercised by scanner and data usage integration tests.
