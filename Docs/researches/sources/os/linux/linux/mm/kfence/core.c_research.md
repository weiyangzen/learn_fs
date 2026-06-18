# File Research: sources/os/linux/linux/mm/kfence/core.c

## Role

KFENCE guarded object allocator and page-fault handler. It allocates and initializes the guarded pool, samples slab allocations, places objects next to guard pages, checks canaries, detects invalid frees/use-after-free/out-of-bounds accesses, manages debugfs and timers, and integrates with slab cache shutdown.

## Key Data

- `kfence_enabled`, `kfence_sample_interval`, `kfence_burst`, `kfence_deferrable`, and `kfence_check_on_panic` control runtime behavior.
- `__kfence_pool` is the guarded memory pool.
- `kfence_metadata` is the visible metadata array; `kfence_metadata_init` is kept private until pool initialization succeeds.
- `kfence_freelist` holds available guarded objects under `kfence_freelist_lock`.
- `kfence_allocation_key` and `kfence_allocation_gate` implement sampled allocation gating.
- `alloc_covered[]` is a counting Bloom filter used to avoid over-covering the same allocation stack when the pool is mostly occupied.
- Debug counters track allocations, frees, active objects, zombie allocations, bugs, and skipped allocation reasons.

## Allocation and Free Flow

- `__kfence_alloc()` rejects objects larger than a page, incompatible GFP zones, DMA caches, `SLAB_SKIP_KFENCE`, disabled state, and covered allocation stacks.
- `kfence_guarded_alloc()` removes metadata from the freelist, trylocks it to avoid printk recursion deadlocks, chooses left/right placement randomly, records allocation state/stack/cache/size/hash, sets slab fields, installs canaries, runs optional init/ctor, optionally stress-protects the object, and updates counters.
- `__kfence_free()` finds metadata and defers freeing through RCU for `SLAB_TYPESAFE_BY_RCU`; otherwise it calls `kfence_guarded_free()`.
- `kfence_guarded_free()` validates the pointer/state, reports invalid free or double free, checks race exclusivity with KCSAN scoped access, restores guard protection after prior reports, marks freed, updates allocation coverage, checks canaries, zeroes if init-on-free is required, protects the object page to catch UAF, and returns metadata to the freelist unless it is a zombie.
- `kfence_shutdown_cache()` turns live objects from a destroying cache into zombie allocations, then clears cache pointers for freed objects from that cache.

## Pool Initialization

- `kfence_alloc_pool_and_metadata()` reserves pool and metadata memory during boot, unless sample interval is zero or KASAN hardware tags are enabled.
- `kfence_init_pool()` calls the architecture pool setup, marks object pages as slab pages, initializes metadata and guard pages, randomizes the freelist, and publishes `kfence_metadata` only after success.
- `kfence_init_pool_early()` finalizes boot-time memblock allocation and avoids kmemleak overlap.
- `kfence_init_late()` supports runtime enablement by allocating contiguous or exact pages after boot.
- `kfence_init_enable()` enables static-key gating, initializes delayed work, registers panic/reboot notifiers, marks KFENCE enabled, and queues the timer.

## Fault Handling

- `kfence_handle_page_fault()` handles faults inside the KFENCE pool.
- Faults on odd pages are guard-page accesses and are reported as out-of-bounds against the closest allocated neighbor.
- Faults on object pages are reported as use-after-free.
- Unknown pool faults are reported as invalid accesses.
- The faulting page is unprotected after reporting so execution can proceed according to the configured report/oops/panic policy.
- If KFENCE is runtime-disabled, faults simply unprotect the page.

## Timer and Interfaces

- `toggle_allocation_gate()` periodically opens the allocation gate, enables static-key sampling when configured, waits for an allocation or shutdown, disables the key, and requeues itself.
- Reboot notifier disables KFENCE and cancels timer work to avoid late static-key IPIs.
- Debugfs exposes `kfence/stats` and `kfence/objects`.
- Panic notifier optionally checks all active canaries.
- Public helpers include `kfence_ksize()`, `kfence_object_start()`, `current_is_khugepaged()` is not here, and KFENCE allocation/free/fault entry points.

## Dependencies

Uses slab internals, page protection architecture hooks, static keys, delayed work, irq work, debugfs, stack traces, random/jhash, memblock/contiguous allocation, panic/reboot notifiers, KASAN hardware-tag detection, KCSAN scoped access, memcg object extensions, and KFENCE reporting.

## Research Notes

KFENCE trades coverage for low overhead. The implementation is defensive about recursion and partially initialized state: page-protection failures disable KFENCE, metadata is published only after full initialization, allocation uses trylock in a rare printk recursion case, and cache destruction intentionally leaks still-live guarded objects as zombies to preserve kernel semantics while improving later diagnostics.
