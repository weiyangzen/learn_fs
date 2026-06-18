# sources/user-network-fs/blobfuse2/component/file_cache/file_cache_constants.go

## Purpose

`file_cache_constants.go` centralizes the metric names used by the file cache stats collector.

## Important APIs, Types, and Functions

It defines four package constants: `cacheUsage`, `usgPer`, `dlFiles`, and `cacheServed`.

## Control Flow

There is no executable control flow. Other file-cache code passes these constants to `fileCacheStatsCollector.UpdateStats`.

## State and Persistence Behavior

The constants themselves are immutable. They affect the labels under which runtime file-cache statistics are recorded.

## Dependencies and Integration Points

The constants are consumed by `cache_policy.go` for cache usage and usage percent, and by `file_cache.go` for files downloaded and files served from cache.

## Risks and Edge Cases

Changing these strings can break monitoring, dashboards, tests, or users that depend on stable stat names. Keeping them in one file reduces the risk of spelling drift.

## Test Signals

There are no direct tests for this file. Indirect coverage comes from file-cache tests that call paths updating stats.
