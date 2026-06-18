# File Research: sources/os/linux/linux/mm/page_frag_cache.c

Page fragment cache allocator for networking and drivers. It provides fast allocation of arbitrary-sized fragments from cached order-0 or higher-order pages, with fragment lifetime tracked through the backing page reference count.

Key responsibilities:
- Encodes a cached page’s virtual address, allocation order, and pfmemalloc state into `page_frag_cache->encoded_page`.
- Refills a page fragment cache from the page allocator, preferring `PAGE_FRAG_CACHE_MAX_ORDER` when supported and falling back to order-0.
- Allocates aligned fragments from the cached page while maintaining `offset` and `pagecnt_bias`.
- Drains page fragment caches and frees backing pages when references drop to zero.
- Exports fragment allocation and free helpers for external users.

Important behavior:
- Higher-order refill avoids direct reclaim, adds `__GFP_COMP`, suppresses warnings, avoids retrying, and avoids emergency reserves; order-0 fallback uses the original GFP mask.
- `__page_frag_alloc_align()` initializes a new page by adding a large reference bias and then decrements that bias for each fragment allocated.
- If the current cached page lacks enough space, the allocator either refills or, if the page is solely owned by the cache, resets its refcount and offset for reuse.
- Requests larger than a page fail when the cache only has an order-0 page, and the existing cache page is retained to avoid worsening memory pressure.
- Pfmemalloc cached pages are freed instead of recycled when exhausted, then the cache refills.
- `page_frag_free()` converts an arbitrary fragment address to the head page and frees the compound allocation when the last fragment reference is dropped.

Dependencies:
- Uses low-level page allocation APIs, page reference counters, compound order, pfmemalloc markers, virtual-to-page conversion, and constants from `linux/page_frag_cache.h`.
- Intended users include networking paths that need fast skb head/frags backing memory.

Notable risks:
- Correctness relies on the encoded-page bit layout matching page alignment and `PAGE_FRAG_CACHE_*` masks.
- The refcount bias scheme must remain compatible with `get_page_unless_zero()` users, so the code deliberately avoids raw `atomic_set()` on freshly refilled pages.
- Callers must free fragments with the matching page-frag free path so backing page references drain correctly.
- Pfmemalloc fragments require care by consumers because such pages come from emergency memory reserves.
