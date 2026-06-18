# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zap_leaf.c

## Role
Implements the bottom half of fat ZAP objects: on-block leaf initialization, byte swapping, chunk allocation, array storage, entry lookup/create/update/remove, normalized-name conflict detection, leaf splitting, and leaf statistics.

## Leaf Layout
- A leaf block contains a header, a hash table of 16-bit chunk indexes, and fixed-size chunks.
- Chunks are typed as free chunks, array chunks, or entry chunks.
- Names and values are stored as linked lists of array chunks; entry chunks point to the name/value chains and carry hash and collision differentiator (`cd`).
- `CHAIN_END` (`0xffff`) terminates hash and array chains.

## Primitive Helpers
- `stv()`/`ldv()` store/load 1-, 2-, 4-, or 8-byte integer values.
- `zap_leaf_byteswap()` swaps headers, hash table entries, and chunk fields for endian conversion.
- `zap_leaf_init()` initializes header magic/type, free list, hash entries, free count, and optionally CD-sorted entry chains.
- `zap_leaf_chunk_alloc()` and `zap_leaf_chunk_free()` manage the free-list and maintain `lh_nfree`.

## Array Handling
- `zap_leaf_array_create()` serializes integer arrays into big-endian byte streams across array chunks.
- `zap_leaf_array_free()` frees an array chain.
- `zap_leaf_array_read()` reads array chains into caller buffers, with fast paths for a single 8-byte integer and byte-string names.
- `zap_leaf_array_match()` compares stored keys with `zap_name_t`, supporting uint64 keys, exact string keys, and normalized matching.

## Entry Operations
- `zap_leaf_lookup()` searches the hash bucket for matching hash and key, returning a `zap_entry_handle_t`.
- `zap_leaf_lookup_closest()` finds the next entry at or after a cursor `(hash, cd)`.
- `zap_entry_read()` reads the value and returns `EOVERFLOW` if caller capacity is too small.
- `zap_entry_read_name()` reads string or uint64-key names.
- `zap_entry_update()` replaces the value chain when enough free chunks are available; otherwise returns `EAGAIN` to trigger leaf split.
- `zap_entry_remove()` unlinks an entry, frees name/value chains, frees the entry chunk, and decrements entry count.
- `zap_entry_create()` finds/assigns a collision differentiator, checks chunk requirements, creates name/value arrays, links into the hash chain sorted by CD, and returns `EAGAIN` or `E2BIG` as appropriate.

## Split And Stats
- `zap_leaf_split()` advances prefix length, assigns sibling prefix, clears/rebuilds hash chains, and transfers entries whose next hash bit is set into the new leaf.
- `zap_leaf_transfer_array()` and `zap_leaf_transfer_entry()` move chunks between leaves while preserving entry content.
- `zap_entry_normalization_conflict()` detects another entry with the same normalized form and different collision differentiator.
- `zap_leaf_stats()` updates histograms for pointer sharing, entries per block, fullness, chunks per entry, and hash bucket depth.

## Important Details
- CD-sorted chains make normalized lookup return the lowest-CD match.
- The code preserves old unsorted-format handling with an O(n^2) CD search fallback.
- `MAX_ARRAY_BYTES` guards array creation against oversized values before chunking.
- Split scanning walks chunks sequentially rather than hash buckets for cache-friendly handling of near-full blocks.
