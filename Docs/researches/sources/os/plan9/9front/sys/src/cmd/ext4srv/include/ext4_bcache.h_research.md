# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bcache.h

Block cache data structure and API header. It defines cached buffer state, cache trees/lists, dirty flags, reference counters, and dynamic cache management functions.

Key behavior:
- `ext4_buf` stores flags, LBA, data pointer, LRU state, reference count, owning cache, tree/list nodes, dirty-list state, and optional write-completion callback.
- `ext4_block` is the public handle pairing logical block ID, cache buffer, and data pointer.
- `ext4_bcache` stores cache capacity, item size, LRU counter, allocated/reference counters, owning block device, shake guard, LBA/LRU red-black trees, and dirty list.
- Defines state bits `BC_UPTODATE`, `BC_DIRTY`, `BC_FLUSH`, and `BC_TMP`.
- Provides inline dirty flag, flag, reference, and dirty-list helpers.
- Declares dynamic init/fini, cleanup, LRU selection, drop/invalidate, lookup, allocation, free, and fullness APIs.

Notable dependencies:
- Uses local `tree.h` and `queue.h`.
- Bound to `ext4_blockdev` and used heavily by transaction/journal code.

Research notes:
- The header's `ref_blocks` comments say referenced data blocks, but the implementation uses it as a count of allocated cache buffers.
- `end_write` is central to checkpoint completion in the journal layer.
