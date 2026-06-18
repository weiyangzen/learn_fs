# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.c

Custom fixed-size FTL mempool.

Behavior:
- `ftl_mempool_create()` allocates DMA memory and initializes an SLIST free list.
- `get`/`put` pop and push elements after validity assertions.
- External-buffer mode creates an uninitialized pool plus bitmap of claimed durable-format entries.
- Before initialization, callers can claim/release durable-format object IDs; `ftl_mempool_initialize_ext()` builds the free list from unclaimed entries.
- Provides conversions between pool pointers, durable-format offsets, and indices.

Risk:
- `ftl_mempool_is_initialized()` returns `inuse_buf == NULL`; the name is correct for initialized normal mode, but the assertion logic can be easy to misread.
- Pointer arithmetic on `void *` relies on compiler extension.
