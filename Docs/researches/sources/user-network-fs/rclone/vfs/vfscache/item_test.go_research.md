# sources/user-network-fs/rclone/vfs/vfscache/item_test.go

## Purpose
Exercises `vfscache.Item` behavior against a test cache and remote, including dirty state, sparse ranges, metadata reload, writeback, random reads, and handle-caching behavior.

## APIs, Flow, And State
Helpers create a cache with cleaner disabled, synchronous writeback, and usually no handle caching. Tests open cache items, write or read ranges, close to trigger store/writeback, then validate remote object contents. Metadata tests remove items from `Cache.item` and force reload from disk. The large read/write test writes a 50 MiB pattern, removes local cache data, then verifies sequential, random, concurrent, and reverse reads rehydrate ranges correctly. Handle-caching tests configure `HandleCaching`, assert descriptors/downloaders remain alive during grace, are reused on reopen, and eventually close.

## Dependencies And Integration
Uses `fstest`, random/pattern readers, `vfscommon.Opt`, direct cache internals, and the in-memory `avInfos` test hook for `AddVirtual`. It is the main regression suite for `item.go` interactions with remote objects, metadata, downloaders, and writeback.

## Risks And Test Signals
The tests are stateful and depend on timing for grace-period expiry, so sleeps can be flaky under heavy load. They give strong signal for range accounting, stale fingerprint invalidation, remote-deleted recovery, reload of dirty cache entries, and concurrent downloader safety. A FIXME notes async writeback coverage is still missing here.
