<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go

## Purpose

This test file validates filesystem behavior for hierarchical namespace buckets. It covers directory listing, deleting explicit and implicit-looking directories, and cache behavior when objects or folders are deleted locally then recreated remotely before TTL expiry.

## Important APIs, Types, and Functions

`HNSBucketTests` composes `fsTest`, `RenameFileTests`, and `RenameDirTests` under a suite with `EnableHns` and atomic rename enabled. `HNSCachedBucketMountTest` configures an HNS fake bucket wrapped in a fast stat cache with directory type caching and file cache defaults. Shared constants define expected file content, HNS type-cache settings, and expected `foo` entries.

## Control Flow

The main HNS suite creates folders and objects in setup, reads `foo` with `os.ReadDir`, removes folders with `os.RemoveAll`, and checks stat failures. The cached suite creates `hns/cache`, creates and stats files or directories through the mount, deletes them, recreates matching objects directly through the uncached bucket, verifies immediate stat still reports not found due to cache, advances cache time past TTL, and verifies the path reappears.

## State and Persistence Behavior

State lives in fake HNS buckets, mounted filesystem state from `fsTest`, metadata/stat caches, and simulated cache time. The tests explicitly rely on cache TTL: local deletion records negative cache state that persists until `cacheClock.AdvanceTime`.

## Dependencies and Integration Points

The file integrates HNS-enabled fs configuration, fake hierarchical buckets, metadata stat/type cache, caching bucket wrappers, file cache config, storage utilities, OS filesystem calls, and rename test suites. It tests interactions among HNS folder APIs, placeholder objects, implicit directory compatibility, and cache invalidation.

## Risks and Edge Cases

HNS buckets represent directories as folders, while gcsfuse also encounters placeholder objects and descendants. Recursive delete must remove the visible directory regardless of backing shape. Cache tests encode the consistency tradeoff where remote recreation remains invisible until TTL expiry, which can surprise users but protects local delete semantics.

## Test Signals

Signals include `os.ReadDir` entry names/types, successful `os.RemoveAll`, expected `no such file or directory` stat errors, and post-TTL successful stats for remotely recreated file and directory paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go -->
