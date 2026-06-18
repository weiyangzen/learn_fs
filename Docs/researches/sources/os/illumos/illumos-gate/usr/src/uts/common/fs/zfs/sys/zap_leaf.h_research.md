# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_leaf.h

This private header defines fatzap leaf-block layout, chunk format, entry handles, and leaf manipulation APIs.

Core definitions:
- `ZAP_LEAF_MAGIC`, 24-byte chunks, chunk-count/hash-table macros, low-water threshold, and hash-table sizing macros define leaf geometry.
- `zap_leaf_phys_t` stores a two-chunk header with block type, prefix, magic, free count, entry count, prefix length, freelist, and flags, followed by hash table and chunks.
- `zap_leaf_chunk_t` is a union of entry chunks, array chunks, and free chunks.
- `zap_leaf_t` stores dbuf user data, leaf rwlock, block ID, block-size shift, and dbuf.
- Inline `zap_leaf_phys()` returns the physical leaf data.
- `zap_entry_handle_t` exposes entry integer count/hash/collision-differentiator/integer size and stores private chunk/leaf references.

Internal API surface:
- Lookup exact name or closest hash/collision differentiator.
- Read value, read name, update value, remove entry, create entry.
- Detect normalization conflicts.
- Initialize, byteswap, split, and collect leaf stats.

Risk-sensitive invariants:
- Comments require `zap_leaf_byteswap()` updates if `zap_leaf_phys_t` changes.
- Chunk chains store names and values across fixed 24-byte chunks; `CHAIN_END` semantics are implementation-critical.
- Split and low-water behavior influence fatzap pointer-table growth and lookup distribution.
