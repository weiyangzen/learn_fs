# File Research: sources/os/linux/linux/mm/percpu-km.c

Contiguous kernel-memory backend for the dynamic per-CPU allocator, intended for NOMMU-style configurations that cannot use vmalloc-backed chunks.

Key responsibilities:
- Provides no-op populate/depopulate and unmap TLB flush hooks because each chunk is allocated as already-contiguous kernel memory.
- Creates chunks by allocating a `pcpu_chunk` descriptor and a power-of-two order block of pages.
- Tags each backing page with its owning per-CPU chunk for reverse lookup.
- Initializes chunk data/base address and marks all pages populated.
- Destroys chunks by freeing the contiguous page block and chunk metadata.
- Converts per-CPU addresses to pages with `virt_to_page()`.
- Verifies allocation info is compatible with the contiguous backend.
- Disables reclaim-based chunk depopulation for this backend.

Important behavior:
- Only one allocation group is supported; NUMA grouping is rejected.
- The actual page allocation is rounded up to a power of two, and the backend warns about wasted pages when the configured chunk size is not naturally aligned.
- It rejects configurations that combine contiguous percpu allocation with a paged first chunk.

Dependencies:
- Uses core percpu allocator helpers, `alloc_pages()`, `__free_pages()`, `order_base_2()`, page-to-chunk tagging, stats hooks, tracepoints, and the global `pcpu_lock`.

Notable risks:
- Memory waste can be significant if chunk size is not a power-of-two multiple of page size.
- The backend cannot reclaim/depopulate chunks, so fragmentation and memory retention differ from the vmalloc backend.
