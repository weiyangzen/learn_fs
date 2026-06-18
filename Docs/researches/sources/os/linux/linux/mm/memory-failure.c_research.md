# File Research: sources/os/linux/linux/mm/memory-failure.c

## Role

Linux high-level hardware memory error and soft-offline handler. It turns machine-check, DAX, PFN-map, hugetlb, LRU, swap-cache, page-cache, and free-page failures into containment actions: mark pages poisoned, unmap users, signal affected tasks, isolate pages from allocators, truncate/evict cache entries, migrate suspicious pages, or report unrecoverable states.

## Key Behavior

- Exposes VM sysctls for early-kill policy, memory-failure recovery panic policy, and soft-offline enablement.
- Maintains global and per-NUMA-node memory failure statistics through `num_poisoned_pages`, memory block poison counters, and `memory_failure_attr_group`.
- Serializes main recovery paths with `mf_mutex`; page lifecycle races are handled with careful refcount acquisition, page locks, retry loops, PCP disable/enable, RCU, and mapping locks.
- Supports an RCU-registered `hwpoison_filter_func` so tests or users can reject selected poison events.
- Builds `to_kill` lists by reverse-mapping anonymous, KSM, file, hugetlb, fsdax, devdax, and registered PFN address-space mappings.
- Sends `SIGBUS` with `BUS_MCEERR_AR` for action-required current-task faults, `BUS_MCEERR_AO` for advisory early-kill users, and `SIGKILL` when corrupted mappings cannot be located or unmapped safely.
- Handles already-poisoned pages by optionally walking the current process page tables to find the poisoned virtual address and signal the accessor.
- Classifies page states through `error_states[]`, then dispatches to handlers for kernel/reserved pages, dirty or clean LRU pages, mlocked/unevictable pages, swap cache pages, huge pages, and unknown states.
- Removes clean page-cache folios with filesystem `error_remove_folio()` when available or mapping eviction otherwise; dirty page-cache errors set mapping `-EIO` before cleanup.
- Keeps dirty swap-cache pages delayed in swap cache so later faults hit poison handling, while clean swap-cache pages can be removed and recovered from backing store.
- Splits large folios before normal handling; failed THP split leads to forced process kill and failed containment because the main handler operates on base pages.
- Handles hugetlb separately under `hugetlb_lock`, tracks raw poisoned subpages in a per-folio list, handles unreliable raw tracking, prevents migration of poisoned huge pages, and dissolves free huge pages when possible.
- Handles ZONE_DEVICE and DAX through device `pgmap->ops->memory_failure()` when available, otherwise falls back to generic DAX process collection, unmap, and kill.
- Provides `register_pfn_address_space()` / `unregister_pfn_address_space()` for memory ranges not backed by `struct page`, using an interval tree to locate affected mappings.
- Provides `memory_failure_queue()` for IRQ-context producers using per-CPU KFIFOs and workqueue processing.
- Provides `unpoison_memory()` for software-injected poison only; it refuses after a real hardware failure and rejects mapped, referenced, reserved, slab, pgtable, offline, or still-mapped pages.
- Provides `soft_offline_page()` to migrate or invalidate still-readable pages without killing tasks, then mark the old page poisoned and remove it from reuse.

## Dependencies

Uses folios, rmap, anon/file interval trees, KSM hooks, DAX locking, dev_pagemap, hugetlb internals, memory hotplug counters, swap cache helpers, migration, LRU isolation, page table walking, shmem detection, memcg uncharge, sysctl registration, trace events, kfifo workqueue plumbing, and architecture hooks such as `arch_memory_failure()`.

## Research Notes

This file is the kernel’s central containment layer for bad physical memory. Its design is intentionally conservative: it favors existing VM locks and slow reverse walks over fast but unsafe shortcuts because failures are rare and can arrive asynchronously against arbitrary page lifecycle states.
