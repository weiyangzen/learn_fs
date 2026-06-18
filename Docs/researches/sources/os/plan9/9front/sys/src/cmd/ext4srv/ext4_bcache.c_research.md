# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bcache.c

Dynamic buffer cache for ext4 logical blocks. It stores cached blocks in red-black trees by LBA and LRU id, tracks references, dirty buffers, writeback callbacks, and invalidation/drop behavior.

Key behavior:
- Initializes and finalizes `ext4_bcache` state with configured item count and block-sized item buffers.
- Uses `RB_GENERATE_INTERNAL` trees for fast lookup by logical block address and eviction by lowest LRU id.
- `ext4_bcache_find_get` returns a referenced buffer if already cached, removing it from LRU/dirty-ready lists while referenced.
- `ext4_bcache_alloc` creates a new `ext4_buf` plus data buffer when no cached buffer exists.
- `ext4_bcache_free` decrements the reference count, re-enters unreferenced buffers into LRU, flushes or dirty-lists dirty buffers, and drops invalidated or temporary buffers.
- `ext4_bcache_invalidate_lba` clears dirty/up-to-date state for cached buffers over an LBA range.

Notable dependencies:
- `ext4_blockdev.c` supplies flushing and cache-shaking logic.
- Red-black tree and singly-linked dirty-list macros are expected from included headers/environment.

Research notes:
- The cache counts allocated buffers through `ref_blocks`, despite the name implying referenced blocks.
- `ext4_bcache_drop_buf` decrements `ref_blocks` even if forcibly dropping a referenced buffer after warning; callers normally avoid that path.
- Cache cleanup iterates all LBA entries, flushes each buffer, then drops it.
- Dirty writeback is coupled to `bdev->cache_write_back`; when writeback is off, dirty buffers flush on last release.
