# File Research: sources/os/linux/linux/mm/percpu-vm.c

Default vmalloc-backed dynamic per-CPU chunk allocator backend. It reserves vmalloc address ranges for chunks and populates/unpopulates physical pages per CPU on demand.

Key responsibilities:
- Resolves chunk virtual addresses back to pages with `vmalloc_to_page()`.
- Maintains a serialized temporary page-pointer array for populate/depopulate operations.
- Allocates one page per possible CPU per chunk page index, preferably on the CPU's node.
- Maps allocated pages into per-CPU vmalloc chunk addresses.
- Unmaps and frees populated pages during depopulation.
- Performs cache and TLB flushes around map/unmap operations.
- Creates chunks by allocating `pcpu_chunk` metadata and grouped vmalloc areas.
- Destroys chunks by freeing vmalloc areas and metadata.
- Decides when chunks should be reclaimed/depopulated based on empty populated pages.

Important behavior:
- The temporary pages array is shared and must be used under `pcpu_alloc_mutex`.
- Population allocates pages first, then maps them; mapping failure frees the newly allocated pages.
- Mapping each CPU's pages also tags pages with the owning chunk for reverse lookup.
- Depopulation gathers currently mapped pages, unmaps the virtual ranges, and frees the physical pages.
- Flushes cover the whole low-to-high per-CPU chunk range rather than issuing per-CPU flushes.
- Reclaim avoids the first and reserved chunks, and considers isolated chunks or chunks with at least a quarter of pages empty when global empty-populated-page pressure is high.

Dependencies:
- Uses vmalloc/vmap APIs, per-CPU group offsets and sizes, CPU/node topology, page-to-chunk tagging, cache/TLB flush helpers, core percpu allocator metadata, stats hooks, tracepoints, and `pcpu_alloc_mutex`.

Notable risks:
- Map/unmap error handling must undo partial CPU mappings and flush TLBs correctly.
- The backend assumes immutable/pre-mapped chunks are not passed to dynamic page lookup paths.
- Reclaim heuristics affect memory footprint and future allocation latency by deciding when populated pages are returned.
