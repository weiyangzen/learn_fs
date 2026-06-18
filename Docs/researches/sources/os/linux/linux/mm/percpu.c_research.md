# File Research: sources/os/linux/linux/mm/percpu.c

## Purpose

`mm/percpu.c` implements Linux's generic percpu memory allocator. It manages static percpu data initialized during boot, optional reserved percpu space for module/static uses, and dynamic percpu allocations served through `pcpu_alloc_noprof()` / `free_percpu()`.

The allocator represents each allocation as an offset inside a per-CPU unit. A `pcpu_chunk` contains one unit per possible CPU; allocating 512 bytes at an offset reserves that same offset in every CPU's unit. The file handles bitmap allocation metadata, chunk slotting by free-contiguous-size, lazy population/depopulation of backing pages, memcg/accounting hooks, and early boot first-chunk construction.

## Main Structures and State

- Global geometry: `pcpu_unit_pages`, `pcpu_unit_size`, `pcpu_nr_units`, `pcpu_atom_size`, `pcpu_unit_map`, `pcpu_unit_offsets`, group offsets/sizes, and `pcpu_base_addr`.
- Chunk state: `pcpu_first_chunk`, optional `pcpu_reserved_chunk`, `pcpu_chunk_lists`, `pcpu_nr_slots`, `pcpu_free_slot`, `pcpu_sidelined_slot`, and `pcpu_to_depopulate_slot`.
- Accounting and reclamation: `pcpu_nr_empty_pop_pages`, `pcpu_nr_populated`, `pcpu_balance_work`, `pcpu_async_enabled`, and `pcpu_atomic_alloc_failed`.
- Locking: `pcpu_lock` protects allocator data structures; `pcpu_alloc_mutex` serializes chunk create/destroy, map extension, and population/depopulation work.

## Allocation Metadata

Chunks use two bitmaps:

- `alloc_map` records allocated allocation units, where each bit represents `PCPU_MIN_ALLOC_SIZE`.
- `bound_map` records allocation boundaries so frees can find the size from an allocation offset.

Metadata blocks (`struct pcpu_block_md`) keep hints:

- `first_free`: earliest free bit.
- `contig_hint` / `contig_hint_start`: largest contiguous free region known for the block or whole chunk.
- `scan_hint`: secondary hint used to avoid full rescans after allocations.
- `left_free` / `right_free`: contiguous free runs at block boundaries.

The allocator is heavily optimized around these hints. `pcpu_find_block_fit()` screens chunks/blocks by hints, `pcpu_find_zero_area()` performs the final bitmap search, and `pcpu_block_update_hint_alloc()` / `pcpu_block_update_hint_free()` update block and chunk metadata after changes.

## Allocation Flow

`pcpu_alloc_noprof()` is the exported allocator implementation.

1. Normalizes GFP flags, size, and alignment.
2. Validates nonzero size, max unit size, power-of-two alignment, and page-sized maximum alignment.
3. Performs memcg precharge for `__GFP_ACCOUNT` non-root cgroup allocations.
4. For sleepable allocations, takes `pcpu_alloc_mutex`; atomic allocations rely only on existing populated backing.
5. Searches the reserved chunk when requested and available.
6. Otherwise scans chunk slots from the requested size class up to the free slot, preferring fuller chunks.
7. If no sleepable allocation fits, creates a new chunk and restarts.
8. Populates missing backing pages for sleepable allocations.
9. Zeroes the allocation in every possible CPU unit.
10. Returns a percpu pointer translated from the chunk base and offset.

Failure handling is careful: failed population frees the reserved bitmap area, memcg precharges are uncharged, atomic failures trigger future balance work, and warnings are rate-limited through `warn_limit`.

## Free and Reclaim Flow

`free_percpu()` translates the percpu pointer back to a canonical address, finds the owning chunk with `pcpu_chunk_addr_search()`, frees the bitmap area with `pcpu_free_area()`, invokes allocation profiling and memcg free hooks, and schedules balance work if the chunk became fully free or reclaimable.

Background balance work (`pcpu_balance_workfn()`) runs under `pcpu_alloc_mutex` and `pcpu_lock` and performs:

- `pcpu_balance_free(false)`: destroy extra fully free chunks.
- `pcpu_reclaim_populated()`: depopulate empty populated pages from isolated chunks.
- `pcpu_balance_populated()`: keep a small reserve of populated empty pages for atomic allocations.
- `pcpu_balance_free(true)`: destroy chunks that became fully depopulated.

The reclaim path isolates chunks before depopulation so allocations do not immediately repopulate pages being reclaimed. TLB flushing is batched per chunk after depopulation.

## First Chunk and Boot Setup

`pcpu_setup_first_chunk()` initializes the allocator from a `struct pcpu_alloc_info` provided by architecture setup code. The first chunk layout is:

`static | reserved | dynamic`

The static region is not managed by allocator chunks. The optional reserved region becomes `pcpu_reserved_chunk`; the dynamic region becomes `pcpu_first_chunk` and is inserted into the normal slot lists.

The file also provides helpers for building first-chunk allocation info:

- `pcpu_build_alloc_info()` groups CPUs by NUMA locality/distance and chooses unit sizing with acceptable waste.
- `pcpu_embed_first_chunk()` allocates percpu units directly in bootmem/linear mapping.
- `pcpu_page_first_chunk()` maps page-sized first-chunk pages into a vmalloc area.
- Generic `setup_per_cpu_areas()` implementations exist for SMP without arch-specific setup and for UP.

## Address Translation and Diagnostics

- `__addr_to_pcpu_ptr()` and `__pcpu_ptr_to_addr()` translate between kernel addresses and percpu pointer encoding.
- `__is_kernel_percpu_address()` / `is_kernel_percpu_address()` test whether an address belongs to the static kernel percpu area.
- `per_cpu_ptr_to_phys()` converts dereferenceable percpu addresses to physical addresses, handling first-chunk direct mapping/vmalloc cases and later chunks through the backend.
- `pcpu_nr_pages()` reports populated backing pages multiplied by unit count for memory reporting.

## Memcg and Allocation Profiling

When `CONFIG_MEMCG` is enabled, the file charges accounted percpu allocations against object cgroups and records the cgroup in per-allocation extension storage (`obj_exts`). Freeing uncharges and updates `MEMCG_PERCPU_B`. With memory allocation profiling enabled, allocation tags are added/subtracted through `pcpu_alloc_tag_alloc_hook()` and `pcpu_alloc_tag_free_hook()`.

## Concurrency and Invariants

- `pcpu_lock` protects chunk lists, bitmaps, hint metadata, empty-page counters, and populated counters.
- `pcpu_alloc_mutex` protects operations that may sleep or manipulate mappings/backing pages.
- Atomic allocations can only use already populated pages.
- Reserved chunks are excluded from normal chunk slot lists and global empty-populated-page counting.
- Immutable first chunks must not be depopulated or destroyed.
- Chunk slots are based on the largest contiguous free hint; fully free chunks live in `pcpu_free_slot`, isolated/reclaim chunks in special slots.

## Filesystem/MM Relevance

Although not filesystem-specific, this allocator backs per-CPU kernel state used throughout VFS, page cache, block I/O, writeback, and filesystem code. Understanding its GFP behavior, memcg charging, and atomic allocation constraints is important when filesystem paths allocate percpu structures under reclaim, filesystem locks, or `GFP_NOFS`/`GFP_NOIO` constraints.
