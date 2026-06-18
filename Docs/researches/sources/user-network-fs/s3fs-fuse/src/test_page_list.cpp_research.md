# sources/user-network-fs/s3fs-fuse/src/test_page_list.cpp

## Purpose
Standalone unit test for `PageList` compression and unloaded-page discovery behavior in the file-cache page tracking layer.

## Important APIs, Types, And Control Flow
The file stubs `CacheFileStat::Open` and `CacheFileStat::OverWriteFile` to avoid full cache-stat persistence. `test_compress` initializes a 42-byte page list, marks ranges loaded, calls `Compress`, and verifies `IsPageLoaded` plus `FindUnloadedPage` start/size results as adjacent and separated ranges are added.

## State And Persistence
The test uses only in-memory `PageList` state. The `CacheFileStat` methods are stubbed to return false, so no cache stat file is opened or overwritten.

## Dependencies And Integration Points
Includes `fdcache_page.h`, `fdcache_stat.h`, and `test_util.h`. It targets cache coherency behavior used by partial downloads/uploads and sparse page tracking.

## Risks And Test Signals
Coverage is narrow: it checks a single size and loaded/unloaded transitions but not modified status, persistence, negative ranges, large page maps, or cache-stat writeback. Its direct signal is unit-level correctness for range compression; integration tests such as cache file stat, sparse upload, and non-boundary writes cover broader effects.
