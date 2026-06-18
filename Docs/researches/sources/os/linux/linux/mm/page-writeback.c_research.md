# File Research: sources/os/linux/linux/mm/page-writeback.c

## Role

Core dirty-page accounting, dirty-throttling, writeback iteration, and folio writeback state management. It computes global, per-node, per-backing-device, and memcg dirty limits; throttles tasks that dirty page cache; starts background writeback; exposes VM writeback sysctls; and provides the folio helpers used by filesystems to mark dirty data and transition folios through writeback.

## Key Behavior

- Defines VM sysctl-controlled dirty parameters: background dirty ratio/bytes, foreground dirty ratio/bytes, highmem dirtyability, periodic writeback interval, dirty expiration interval, and deprecated laptop mode.
- Maintains `global_wb_domain`, writeback completion fractions, dirty limits, dirty ratelimits, per-CPU dirty throttle leak accounting, and BDI min/max dirty ratios.
- Supports cgroup writeback through paired dirty-throttle contexts: a global context and an optional memcg context. In cgroup mode, memcg domains use memcg-specific writeback domains and completion counters; without cgroup writeback, the memcg context helpers compile to inert stubs.
- `global_dirtyable_memory()` and `node_dirtyable_memory()` compute dirtyable memory from free pages plus active/inactive file pages minus reserves, with optional highmem exclusion. `domain_dirty_limits()` converts ratio or byte sysctls into background and foreground thresholds and gives realtime/deadline tasks a modest reserve boost.
- Sysctl handlers enforce mutual exclusion between ratio and byte modes, validate that byte limits fit in dirty-throttling counters, and refresh ratelimit state when foreground limits change.
- Writeback completion tracking uses fprop fractions. `wb_domain_writeout_add()`, `__wb_writeout_add()`, `writeout_period()`, `wb_domain_init()`, and `wb_domain_exit()` maintain aged proportions of each writeback device/domain's completed writeout.
- BDI dirty share controls enforce global minimum-ratio sum limits, max ratio bounds, conversion to/from byte limits, and strict-limit mode for backends such as FUSE that must be throttled against small per-BDI caps.
- `__wb_calc_thresh()` assigns a writeback instance's share of a domain threshold based on recent completion fractions plus BDI min/max ratios. It grants inactive devices a small usable threshold and honors strict limits.
- `wb_position_ratio()` computes a fixed-point position-control ratio from global dirty state and per-writeback dirty state. It uses a cubic polynomial around global setpoints, special strict-limit control against per-WB counters, and linear per-WB correction based on write bandwidth and dirty share.
- `wb_update_write_bandwidth()`, `update_dirty_limit()`, `wb_update_dirty_ratelimit()`, and `__wb_update_bandwidth()` estimate write bandwidth, smooth dirty limits, and update the base dirty ratelimit so concurrent dirtying tasks converge toward device writeout capacity.
- `balance_dirty_pages()` is the core throttling loop. It computes global and memcg limits, starts background writeback above background thresholds, exits quickly when all active domains are below freerun ceilings, otherwise calculates selected domain position ratio, updates bandwidth, computes task ratelimit and sleep time, sleeps in `TASK_KILLABLE` unless `BDP_ASYNC` asks for `-EAGAIN`, and updates per-task dirty polling intervals.
- `balance_dirty_pages_ratelimited_flags()` is called by dirtier paths after newly dirtying pages. It chooses the inode's current cgroup writeback instance, applies per-task and per-CPU ratelimits, absorbs dirty counts leaked by exited tasks, and invokes `balance_dirty_pages()` when the threshold is reached. `balance_dirty_pages_ratelimited()` is the exported synchronous wrapper.
- `wb_over_bg_thresh()` tells flusher code whether a writeback instance remains over global or memcg background thresholds, using reclaimable dirty pages without counting pages already under writeback.
- `writeback_set_ratelimit()` derives the global ratelimit interval from the dirty threshold and online CPU count; CPU hotplug callbacks refresh it. `page_writeback_init()` initializes the global domain, registers CPU hotplug callbacks, and registers VM sysctls.
- `tag_pages_for_writeback()` scans an address_space xarray and marks dirty pages with `PAGECACHE_TAG_TOWRITE` to bound writeback work and avoid livelock against ongoing dirtying.
- `writeback_iter()` is the modern filesystem writeback iterator. It initializes range/cyclic state, optionally tags pages for integrity writeback, returns locked dirty folios prepared by `folio_prepare_writeback()`, decrements `nr_to_write`, preserves the first integrity-writeback error while continuing tagged work, updates `mapping->writeback_index`, and requires callers to iterate to `NULL`.
- `do_writepages()` calls the filesystem `writepages` operation when present, throttles and retries `-ENOMEM` during synchronous writeback, and periodically updates writeback bandwidth.
- Dirty marking helpers include `noop_dirty_folio()`, `__folio_mark_dirty()`, `filemap_dirty_folio()`, `folio_mark_dirty()`, and `folio_mark_dirty_lock()`. They set folio and xarray dirty state, attach inodes to writeback instances, update LRU/node/zone/WB stats, account task IO, increment per-task dirty counters, and mark inodes dirty.
- `folio_redirty_for_writepage()` lets a filesystem decline writeback, increments skipped pages, redirties the folio, and reverses dirtied accounting so writeback refusal does not look like new dirtying.
- Cleaning helpers `folio_account_cleaned()`, `__folio_cancel_dirty()`, and `folio_clear_dirty_for_io()` remove dirty accounting safely. `folio_clear_dirty_for_io()` serializes against PTE dirtying through folio locking, uses `folio_mkclean()` side effects to capture mapped dirtiness, and leaves temporary xarray-tag/folio-flag incoherency only while the folio is locked.
- Writeback state helpers `__folio_start_writeback()` and `__folio_end_writeback()` set and clear `PG_writeback`, manage xarray writeback/TOWRITE/DIRTY tags, update WB and global stats, mark or clear superblock inode-writeback state, update writeout completion fractions, track writeback-inode counts, and schedule deferred bandwidth updates.
- `folio_wait_writeback()`, `folio_wait_writeback_killable()`, and `folio_wait_stable()` wait on active writeback, with the stable-write helper gated by backing-device requirements.

## Dependencies

Uses address_space xarrays and pagecache tags, folio APIs, backing-dev writeback structures, memcg writeback domains, fprop completion accounting, sysctl, CPU hotplug, scheduler IO sleep, VM and node counters, inode writeback attachment, superblock writeback markers, tracepoints, filesystem `address_space_operations`, reclaim throttling, and architecture stable-page accessibility hooks.

## Research Notes

This file is both control theory and accounting infrastructure. Dirty throttling balances user-visible write throughput against memory pressure by adapting to actual writeback completion rates rather than static device weights. Correctness depends on keeping folio dirty flags, xarray tags, writeback flags, inode state, and per-WB/global/memcg counters synchronized across filesystem writeback, memory reclaim, page faults, and truncation. The most subtle areas are temporary dirty-tag incoherency during `folio_clear_dirty_for_io()`, memcg/global dual-domain throttling, strict-limit devices, and the requirement that `writeback_iter()` callers drain the iterator to completion.
