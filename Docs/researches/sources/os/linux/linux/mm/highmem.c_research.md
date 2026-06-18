# File Research: sources/os/linux/linux/mm/highmem.c

## Purpose

`highmem.c` implements common Linux high-memory mapping support. It provides permanent highmem mappings through the pkmap area, local per-task/per-CPU kmap mappings through fixmap slots, highmem page zeroing helpers, and optional hashed `page_address()` tracking for architectures that cannot store direct virtual addresses in `struct page`.

## Major Responsibilities

- Count free and total highmem pages.
- Implement `kmap_high()`, `kmap_high_get()`, and `kunmap_high()` for schedulable highmem mappings.
- Maintain `pkmap_count[]`, `pkmap_page_table`, `kmap_lock`, wait queues, and TLB flush handling for pkmap slots.
- Translate kmap virtual addresses back to pages in `__kmap_to_page()`.
- Implement `kmap_local_page()` internals using fixmap PTE slots, migration disable, and per-task `kmap_ctrl`.
- Save and restore local kmap mappings across context switches.
- Provide `zero_user_segments()` for zeroing one or two ranges inside a possibly compound page.
- Optionally implement hashed `page_address()` and `set_page_address()` mappings.

## Permanent Highmem Mapping Path

The `CONFIG_HIGHMEM` section manages the pkmap area. `pkmap_count[]` is intentionally not a simple reference count:

- `0` means the slot is usable and has not been mapped since the last TLB flush.
- `1` means no active users, but the stale mapping still requires a TLB flush before reuse.
- Values above `1` mean active users, with `count - 1` users.

`map_new_virtual()` searches for a usable pkmap slot, flushing zero-count-stale slots with `flush_all_zero_pkmaps()` when the colored index wraps. If no slot is available, it sleeps on the color-specific wait queue until another task unmaps a slot. Once a slot is selected, it installs a PTE in `pkmap_page_table`, sets `pkmap_count` to `1`, and records the virtual address with `set_page_address()`.

`kmap_high()` locks `kmap_lock`, reuses an existing mapping from `page_address()` when present, otherwise calls `map_new_virtual()`, then increments the slot count. `kunmap_high()` decrements the count and wakes waiters when the slot becomes inactive but still pending TLB flush.

Architectures can override color selection and wait queues with `get_pkmap_color()`, `get_next_pkmap_nr()`, `no_more_pkmaps()`, `get_pkmap_entries_count()`, and `get_pkmap_wait_queue_head()`.

## Address Translation and Zeroing

`__kmap_to_page()` recognizes:

- pkmap addresses and translates them through `pkmap_page_table`.
- local kmap fixmap addresses and compares against the current task's saved `kmap_ctrl.pteval[]`.
- ordinary lowmem direct-map addresses via `virt_to_page()`.

`zero_user_segments()` zeroes up to two byte ranges across a page or compound page. It maps individual subpages with `kmap_local_page()` only when a segment overlaps that subpage, unmaps with `kunmap_local()`, and flushes the dcache for changed subpages.

## Local Kmap Implementation

Under `CONFIG_KMAP_LOCAL`, local mappings are built from fixmap slots. `kmap_local_idx_push()` and `kmap_local_idx_pop()` maintain a per-task nesting index, with `CONFIG_DEBUG_KMAP_LOCAL` optionally leaving guard slots.

`__kmap_local_pfn_prot()`:

1. Disables migration so the local virtual address remains CPU-stable.
2. Disables preemption while selecting and installing a fixmap PTE.
3. Computes the architecture-specific slot index.
4. Installs the PTE with `arch_kmap_local_set_pte()`.
5. Stores the PTE in `current->kmap_ctrl.pteval[]`.
6. Re-enables preemption and returns the fixmap virtual address.

`__kmap_local_page_prot()` avoids creating a mapping for lowmem pages unless debug force-map mode requires one. It can also reuse `arch_kmap_local_high_get()` before installing a new local PTE.

`kunmap_local_indexed()` validates that the unmap address matches the current nesting slot, clears the PTE, clears the saved PTE value, pops the index, re-enables preemption, and re-enables migration. It also handles mappings obtained from `kmap_high_get()` and warns on unexpected user-range addresses.

## Context Switch Handling

`__kmap_local_sched_out()` clears all active local kmap PTEs for the outgoing task without changing the saved nesting index. This is safe with interrupts because nested interrupt kmaps use unused slots and restore their own index.

`__kmap_local_sched_in()` reinstalls saved PTEs for the incoming task. `kmap_local_fork()` warns and clears inherited kmap state if a task is forked while local mappings are active.

## Hashed Page Address Support

When `HASHED_PAGE_VIRTUAL` is defined, highmem virtual-address tracking uses a small hash table:

- `struct page_address_map page_address_maps[LAST_PKMAP]`
- `struct page_address_slot page_address_htable[1 << PA_HASH_ORDER]`

`page_address()` returns direct lowmem addresses for lowmem pages and otherwise searches the hashed list for a highmem page. `set_page_address()` inserts or removes page-to-virtual mappings under the bucket lock. `page_address_init()` initializes all hash buckets.

## Integration Points

This file supports many subsystems that need temporary kernel access to highmem pages, including the GUP test long-term read path, block I/O helpers, page-cache operations, and architecture code. Correctness depends on strict nesting, migration/preemption handling, TLB flushing before pkmap reuse, and architecture hooks for aliasing caches or non-linear kmap PTE layouts.
