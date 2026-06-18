# sources/storage-engines/rocksdb/cache/clock_cache.h

## Purpose
Declares the internal structure and public cache classes for RocksDB HyperClock cache. The header is unusually explanatory: it documents the design goal of a mostly lock-free/read-optimized CLOCK cache for block-cache use, contrasts fixed and automatic table sizing, specifies key limitations, and lays out the packed reference-count and slot-state protocol used by the implementation.

## Important APIs, Types, And Functions
`ClockHandleBasicData` is the cache handle payload: object pointer, item helper, reversible 128-bit key hash, and total charge. `ClockHandle` adds the atomic `SlotMeta` word. `SlotMeta` defines acquire/release counters plus hit, occupied, shareable, and visible flags, with convenience methods for empty, construction, visible, and invisible states.

`BaseClockTable` declares shared insertion, standalone-handle creation, capacity and usage accounting, reference acquisition, eviction accounting, and diagnostic counters. `FixedHyperClockTable` declares the fixed open-addressed table, its 64-byte `HandleImpl`, displacement counters, load-factor constants, lookup/insert/release/erase APIs, and occupancy-limit helpers. `AutoHyperClockTable` declares the mmap-backed growing linear-hash table, its decorated `NextWithShift` chain pointers, rewrite-lock-based chain maintenance, growth, purge, lookup, eviction, and table-size APIs.

`ClockCacheShard<TableT>` adapts either table to the `CacheShardBase` concept and supplies hashed-key computation, reverse hashing, insert, standalone creation, lookup, ref/release, erase, usage, pinned usage, occupancy, and scanning APIs. `BaseHyperClockCache<Table>` adapts shards to `ShardedCache`. `FixedHyperClockCache` and `AutoHyperClockCache` provide concrete cache names and diagnostics.

## Control Flow
The header defines the intended lifecycle. Insert reserves occupancy/usage, chooses an empty slot, initializes payload while the slot is under construction, then publishes it as visible with the initial priority countdown encoded into counters. Lookup computes a reversible hash from the 16-byte block-cache key, finds a slot or chain entry, increments the acquire counter, validates visible key equality, and returns a pinned handle. Release either increments the release counter, or for `useful=false` decrements acquire to undo the use signal. Erase marks visible entries invisible or takes construction ownership and frees them if unreferenced.

CLOCK eviction sweeps candidate entries. Unreferenced visible entries with positive countdown are aged by decrementing the counters; unreferenced visible entries with zero countdown and unreferenced invisible entries are transitioned to construction for deletion. Referenced entries are counted as pinned and skipped. Fixed tables sweep direct slots; auto tables sweep chains and purge construction entries under per-chain rewrite locks.

The fixed variant keeps a non-resizable table sized from `capacity`, `estimated_entry_charge`, metadata charge policy, and a target load factor. The auto variant uses linear hashing over a pre-reserved mmap range, starts small, grows incrementally as occupancy rises, and keeps shift-tagged chain links so lookup remains safe while growth splits chains.

## State And Persistence Behavior
All state is in process memory. There is no file or manifest persistence. Handles carry value ownership and call `CacheItemHelper::del_cb` through `FreeData`. The packed atomic `SlotMeta` is the core consistency state: empty slots have no defined payload, construction slots are exclusively owned, visible slots can be found by lookup, invisible slots preserve existing references but hide from lookup, and standalone handles are heap-allocated invisible entries outside table occupancy.

Usage accounting distinguishes table-tracked `usage_`, `standalone_usage_`, occupancy, capacity, strict-capacity mode, and metadata charge policy. Auto-table persistence-like behavior is limited to the lifetime of an anonymous memory mapping; growing only maps/uses more of the reserved address space and may increase metadata charge.

## Dependencies And Integration Points
The header depends on `cache/cache_key.h`, `cache/sharded_cache.h`, `rocksdb/cache.h`, `port/mmap.h`, `util/atomic.h`, `util/bit_fields.h`, and math utilities. It is compiled into the RocksDB cache subsystem and connected to users through `HyperClockCacheOptions`, `ShardedCache`, `CacheWithSecondaryAdapter`, block-cache helpers, memory allocators, cache eviction callbacks, and tests that friend `clock_cache::ClockCacheTest`.

The fixed and auto classes share one shard/cache adapter layer, so public cache behavior is mostly uniform while table organization differs. Key hashing is deliberately lossless for 16-byte block-cache keys, allowing eviction callbacks and `ApplyToHandle` to reconstruct the original key from `UniqueId64x2`.

## Risks And Edge Cases
The documented limitations are material: HyperClock cache supports only exact 16-byte keys, does not guarantee insert overwrite for an existing key, enforces priorities less aggressively than LRU, and may free erased or duplicate entries only on later eviction. High shard counts, small capacities, large entries, and many pinned entries can make eviction expensive or ineffective. Internal counters can overflow if simultaneous references are extremely high.

Fixed HyperClock has a sizing risk because the table does not resize; an inaccurate estimated entry charge can waste memory, hit occupancy limits before capacity, or force standalone handles. Auto HyperClock removes that fixed sizing issue but introduces localized waits for chain rewrite locks during growth/removal and depends on careful shift-tagged chain invariants.

## Test Signals
The header's friend hooks and `TEST_` methods are used by `cache/lru_cache_test.cc` typed `ClockCacheTest` cases. Observable signals include `GetUsage`, `GetStandaloneUsage`, `GetOccupancy`, `GetOccupancyLimit`, `GetTableSize`, pinned usage scans, yield counts, eviction-effort-exceeded counts, and diagnostic logging from the concrete cache classes. General cache API tests in `cache/cache_test.cc` must account for HyperClock-specific behavior, especially 16-byte keys and weak overwrite semantics.
