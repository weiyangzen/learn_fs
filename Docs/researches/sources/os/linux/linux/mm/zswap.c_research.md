# File Research: sources/os/linux/linux/mm/zswap.c

## Purpose

`zswap.c` implements zswap, a compressed RAM cache for swap pages. When a folio is being swapped out, zswap can compress each page and store it in a zsmalloc pool instead of immediately writing it to the swap device. On swapin, zswap decompresses the page from RAM. Under pressure or pool limits, it writes cold entries back to the real swap device.

## Tunables And Global State

Module parameters control:

- `enabled`
- `compressor`
- `max_pool_percent`
- `accept_threshold_percent`
- `shrinker_enabled`

`zswap_ever_enabled` is a static key used to avoid work when zswap was never active. `zswap_enabled` is the runtime gate. `zswap_init_state`, `zswap_init_lock`, and `zswap_has_pool` coordinate setup and parameter changes.

Statistics include stored pages, stored incompressible pages, pool limit hits, writebacks, reclaim failures, compression failures, poor compression, decompression failures, allocator failures, and metadata allocation failures. VM events `ZSWPIN`, `ZSWPOUT`, and `ZSWPWB` are counted on load, store, and writeback.

## Pools And Compression Contexts

`struct zswap_pool` combines:

- a zsmalloc `zs_pool`
- per-CPU async-compression contexts
- a percpu refcount
- RCU list membership
- deferred release work
- selected compressor name

Pool creation initializes zsmalloc, allocates per-CPU crypto contexts, registers CPU hotplug preparation callbacks, and initializes a percpu ref. Compressor parameter changes can create a new current pool, reuse an old matching pool by resurrecting its percpu ref, and retire the previous current pool by killing its ref. Empty retired pools are removed from the RCU list and destroyed after `synchronize_rcu()`.

Each CPU's `crypto_acomp_ctx` owns an acomp transform, request, wait object, temporary buffer, and mutex. `zswap_cpu_comp_prepare()` allocates these per pool and CPU.

## Entry Indexing And LRU

Each compressed page is tracked by `struct zswap_entry`:

- swap entry and xarray offset
- compressed length
- `referenced` second-chance bit
- pool pointer and zsmalloc handle
- objcg charge owner
- LRU list node

For each swap type, `zswap_swapon()` allocates an array of xarrays, one per 64M swap-space page range. `swap_zswap_tree()` maps a swap entry to the proper xarray. `zswap_swapoff()` verifies entries are gone and frees the xarray array.

`zswap_list_lru` is a global NUMA-aware, memcg-aware LRU for writeback candidates. Entries are added and deleted using memcg-aware list_lru helpers under RCU to tolerate memcg offlining.

## Store Path

`zswap_store()` requires a locked swapcache folio. It checks runtime enablement, objcg zswap allowance, pool limits, current pool availability, and memcg list_lru allocation. It then stores each base page in the folio using `zswap_store_page()`.

`zswap_store_page()` allocates entry metadata, compresses and stores the page, inserts the entry into the swap xarray, frees any stale old entry, grabs pool and objcg references, charges zswap memory, initializes entry fields, and adds the entry to the LRU.

`zswap_compress()` uses the current CPU's acomp context to compress into a per-CPU buffer. If compression fails, produces zero length, or does not shrink below `PAGE_SIZE`, zswap either rejects the page when memcg zswap writeback is disabled or stores the original page uncompressed with `length == PAGE_SIZE` so LRU writeback order is preserved. Compressed or uncompressed bytes are allocated in zsmalloc with NOWAIT/NORETRY/MOVABLE flags and written with `zs_obj_write()`.

If store fails or zswap is disabled, `zswap_store()` invalidates stale zswap entries for all page offsets covered by the folio so later writeback cannot overwrite newer swapfile data.

## Load And Invalidation

`zswap_load()` looks up the entry for a locked swapcache folio. Large folios are rejected because zswap may only have partial per-page entries. On success it decompresses into the folio, marks it uptodate and dirty, counts `ZSWPIN`, erases the entry from the xarray, frees zswap storage, and unlocks the folio. Missing entries return `-ENOENT` with the folio still locked.

`zswap_invalidate()` erases and frees a single entry, used when swap slots are invalidated.

`zswap_decompress()` reads the zsmalloc object as a one- or two-entry scatterlist. Uncompressed `PAGE_SIZE` entries are copied directly; compressed entries go through acomp decompression. It validates the output length and records decompression failures.

## Writeback And Shrinking

`zswap_writeback_entry()` resumes swap writeback for one compressed entry. It pins the swap device, allocates or finds a swapcache folio, skips if swapin or another shrinker already populated it, validates that the xarray still points to the same entry, decompresses into the folio, erases and frees the zswap entry, marks the folio uptodate and reclaim, and calls `__swap_writepage()`.

The shrinker uses three controls:

- A second-chance `referenced` bit, cleared on first scan and written back on later scan.
- Per-lruvec disk swapin counters to detect overshrinking and reduce reclaimable estimates.
- Compression ratio scaling, so highly compressed memory is less aggressively written back.

`zswap_shrinker_count()` computes reclaimable entries from list_lru count, memcg or global zswap backing size, stored pages, disk swapins, and compression savings. It refuses to run without IO/FS permission. `zswap_shrinker_scan()` walks the LRU and calls `shrink_memcg_cb()`.

When the pool limit is reached, `zswap_check_limits()` sets `zswap_pool_reached_full`; failed stores can queue `zswap_shrink_work`. `shrink_worker()` round-robins online memcgs with zswap writeback enabled and writes entries back until the accept threshold is reached or retry limits are hit. `zswap_memcg_offline_cleanup()` advances the shrink cursor if a memcg is being offlined.

## Debugfs And Initialization

With debugfs, `zswap_debugfs_init()` creates `zswap/` counters for rejection, decompression, writeback, total pool size, stored pages, and stored incompressible pages.

`zswap_setup()` creates the entry cache, registers CPU hotplug multi-state for compression context setup, creates the shrink workqueue, allocates and registers the shrinker, initializes the memcg-aware list_lru, creates the fallback/current pool, enables the static key if a pool exists, initializes debugfs, and marks setup successful. `zswap_init()` is a late initcall so crypto algorithms are available.

## Integration Points

`zswap.c` integrates swapcache, swap devices, zsmalloc, crypto acomp, memcg/objcg charging, list_lru, shrinkers, CPU hotplug, debugfs, vm events, and folio state. It depends on zsmalloc object APIs and contributes zswap event names through `vmstat.c`.

## Concurrency And Invariants

- Store and invalidation are serialized by the folio lock for a swap slot.
- Writeback drops LRU locks before IO but validates the xarray still contains the same entry before dereferencing.
- Pool list traversal is RCU protected; pool lifetime is guarded by percpu refs.
- Entry publication order matters: an entry enters the xarray before it is added to the LRU, so writeback cannot see partially initialized LRU entries.
- Large folio load is rejected because per-page zswap entries do not represent a whole large folio coherently.
- Memcg offlining must not leave `zswap_next_shrink` holding a stale reference.

## Risks And Test Focus

Risks include stale entry writeback overwriting newer swap data, compressor parameter races, per-CPU crypto hotplug failures, objcg charge leaks, memcg offline shrink cursor bugs, uncompressed-entry accounting drift, and large-folio partial-store hazards. Tests should cover store/load/invalidate, stale replacement, swapoff cleanup, writeback races with swapin, pool limit shrink work, compressor switching, memcg writeback disabled behavior, CPU hotplug, and debugfs/stat counter sanity.
