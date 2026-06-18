# sources/user-network-fs/blobfuse2/component/file_cache/cache_policy.go

## Purpose

`cache_policy.go` defines the policy interface and shared helpers for file cache eviction policies.

## Important APIs, Types, and Functions

`cachePolicyConfig` carries temp path, timeout, max eviction count, size thresholds, lock map, and trace flag. `cachePolicy` defines lifecycle, config update, validity/invalidation/purge notifications, cache membership, and policy name methods. `getUsagePercentage` computes current cache usage relative to configured maximum, and `deleteFile` removes a file with permission and missing-file handling.

## Control Flow

`getUsagePercentage` rejects invalid max size by logging and returning zero, calls `common.GetUsage`, converts usage to a percentage, updates the file cache stats collector with current MB and percent, and returns the value. `deleteFile` attempts `os.Remove`; permission errors trigger chmod to `0666` and retry, not-found errors are treated as success, and other errors are returned.

## State and Persistence Behavior

The file has no durable state of its own. `getUsagePercentage` mutates metrics in `fileCacheStatsCollector`; `deleteFile` mutates the local filesystem and may change permissions before removal.

## Dependencies and Integration Points

It depends on Blobfuse `common`, `log`, and `stats_manager`, plus `os`. `lru_policy.go` implements `cachePolicy`, and `file_cache.go` constructs policy configs and calls policy methods around file operations.

## Risks and Edge Cases

`fileCacheStatsCollector` must be initialized before `getUsagePercentage` updates stats. Usage is directory-size based and can be expensive on large caches. `deleteFile` broadens permissions to remove files, which is intentional for cache cleanup but security-sensitive if paths escape the cache root.

## Test Signals

`cache_policy_test.go` covers usage measurement, percentage calculation including zero max size, and deleting a missing path without error.
