# File Research: sources/os/linux/linux/mm/util.c

This file is a broad mm utility collection. It provides allocation/string duplication helpers, userspace memory duplication helpers, mmap layout randomization, locked-memory accounting, mmap entry wrappers, folio/page helpers, overcommit accounting, command-line extraction, page-offline synchronization, mmap descriptor compatibility helpers, mmap action dispatch, and page snapshot support.

Memory/string helpers:
- `kfree_const()` frees only non-rodata pointers.
- `kstrdup()`, `kstrdup_const()`, `kstrndup()`, `kmemdup_noprof()`, `kmemdup_array()`, `kvmemdup()`, and `kmemdup_nul()` implement common kernel duplication patterns.
- `memdup_user()`, `vmemdup_user()`, `strndup_user()`, and `memdup_user_nul()` allocate kernel memory and copy user buffers with correct `ERR_PTR()` failure signaling.
- `user_buckets` is initialized for user-copy duplication allocation buckets.

Mapping/layout helpers:
- `vma_is_stack_for_current()` tests whether a VMA contains the current stack pointer.
- `vma_set_file()` swaps a VMA file reference during initial setup.
- `randomize_stack_top()` and `randomize_page()` provide stack and page-aligned ASLR helpers.
- `arch_pick_mmap_layout()` selects legacy or top-down mmap layout based on personality, stack rlimit, randomization, and architecture configuration.
- `vm_mmap_pgoff()` and `vm_mmap()` wrap `do_mmap()` with security, fsnotify, mmap locking, userfaultfd completion, and population handling.
- `vm_mmap_shadow_stack()` maps architecture shadow stacks when enabled.

Accounting and overcommit:
- `__account_locked_vm()` and `account_locked_vm()` update `mm->locked_vm` with `RLIMIT_MEMLOCK` enforcement.
- Sysctls cover `overcommit_memory`, `overcommit_ratio`, `overcommit_kbytes`, `user_reserve_kbytes`, and `admin_reserve_kbytes`.
- `vm_commit_limit()` computes strict overcommit allowance from RAM, hugetlb pages, swap, and ratio/kbytes settings.
- `vm_memory_committed()` exports the committed-as counter.
- `__vm_enough_memory()` enforces overcommit policies and rolls back committed accounting on failure.

Folio/page helpers:
- `folio_anon_vma()` returns an anon_vma from encoded folio mapping state.
- `folio_mapping()` resolves page-cache, swap-cache, or NULL mapping for a folio.
- `folio_copy()` and `folio_mc_copy()` copy all pages in a folio, with machine-check-aware copy support.
- `memcmp_pages()` maps and compares two pages.
- `flush_dcache_folio()` falls back to per-page dcache flushing if not architecture-provided.
- `snapshot_page()` safely captures page and folio metadata into a `page_snapshot`, marking snapshots unfaithful if compound state is unstable.
- `page_range_contiguous()` validates memmap contiguity for sparsemem without vmemmap.

Diagnostics and synchronization:
- `get_cmdline()` reads a task’s argv/env memory using `access_process_vm()`, including setproctitle-style handling.
- `mem_dump_obj()` reports object provenance through slab/vmalloc helpers or coarse memory type classification.
- `page_offline_freeze()`, `page_offline_thaw()`, `page_offline_begin()`, and `page_offline_end()` coordinate readers with drivers setting `PageOffline()`.

mmap descriptor compatibility/actions:
- `compat_set_desc_from_vma()` builds a `vm_area_desc` from an existing VMA for stacked mmap compatibility.
- `compat_set_vma_from_desc()` is declared inline in `vma.h` and used here by `__compat_vma_mmap()`.
- `compat_vma_mmap()` lets legacy `.mmap()`-style stacked drivers invoke underlying `.mmap_prepare()` logic.
- `mmap_action_prepare()` dispatches preparatory actions such as remap PFN, IO remap, simple IO remap, and map-kernel-pages.
- `mmap_action_complete()` completes supported actions and funnels cleanup through `mmap_action_finish()`.
- `mmap_action_finish()` calls `vm_ops->mapped`, success/error hooks, releases temporary rmap locks, and unmaps the VMA on post-map failure when not in compatibility mode.
- `folio_pte_batch()` is a wrapper for detecting same-folio PTE runs in MMU builds.

Research notes:
- This file bridges core mm policy with user-facing syscall-like behavior, especially mmap and overcommit.
- Several functions are compatibility scaffolding for converting drivers from `.mmap()` to `.mmap_prepare()`.
- Error cleanup is careful because mmap action completion can occur after a VMA has become visible.
