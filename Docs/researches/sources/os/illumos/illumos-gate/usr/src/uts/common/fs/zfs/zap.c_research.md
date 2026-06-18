# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zap.c

## Role
Implements the top half of fat ZAP objects: the extendable hash directory, pointer table growth, leaf lookup/splitting, high-level fat-ZAP add/update/remove/lookup, cursor retrieval, and stats. Leaf block internals live in `zap_leaf.c`; micro-ZAP/public wrappers live in `zap_micro.c`.

## Data Structure
- A fat ZAP has a header block with `zap_phys_t`, an embedded or external pointer table, and one or more leaf blocks.
- The pointer table maps high hash prefixes to leaf block ids. Its length is a power of two controlled by `zt_shift`.
- Leaves hold entries with matching hash prefixes and are split when they run out of space.

## Pointer Table Mechanics
- `fzap_upgrade()` converts a micro object into a fat ZAP header, initializes embedded pointer table entries to leaf block 1, and creates the first leaf.
- `zap_grow_ptrtbl()` grows from embedded to external table or doubles an external table through `zap_table_grow()`.
- `zap_table_grow()` copies one block of an old table per invocation into a new doubled table, supporting incremental pointer-table growth.
- `zap_table_store()` updates both current and partially grown `nextblk` tables so in-progress growth remains consistent.
- `zap_idx_to_blk()` and `zap_set_idx_to_blk()` abstract embedded vs external table access.

## Leaf Lifecycle
- `zap_create_leaf()` allocates a new leaf block, installs a dbuf user, initializes leaf state, and increments the leaf count.
- `zap_open_leaf()` creates/interns a `zap_leaf_t` for an existing dbuf and validates structural invariants.
- `zap_get_leaf_byblk()` and `zap_deref_leaf()` hold and lock the target leaf for a hash.
- `zap_expand_leaf()` handles full leaves: upgrades to writer if needed, grows the pointer table if prefix length reached table shift, creates a sibling leaf, splits entries, and retargets sibling pointer-table slots.
- `zap_put_leaf_maybe_grow_ptrtbl()` opportunistically grows the pointer table after releasing a low-free leaf or during pending growth.

## Attribute Operations
- `fzap_lookup()` validates name/size, dereferences the leaf, finds the entry, reads value/name, and optionally reports normalization conflict.
- `fzap_add()`/`fzap_add_cd()` create entries, split leaves on `EAGAIN`, and increment `zap_num_entries`.
- `fzap_update()` updates or creates an entry, splitting if the leaf lacks chunk space.
- `fzap_length()` reports stored integer size/count.
- `fzap_remove()` removes an entry and decrements `zap_num_entries`.
- Size validation permits integer sizes 1, 2, 4, or 8 and caps value length at `ZAP_MAXVALUELEN`.

## Helpers And Iteration
- `zap_create_link*()` creates a ZAP object and links it into a parent ZAP.
- `zap_join*()` variants copy or merge one-integer entries between ZAPs.
- `zap_*_int*()` helpers represent integer keys as hex strings.
- `zap_increment()` and `zap_increment_int()` adjust numeric values, removing entries when the result becomes zero.
- `fzap_cursor_retrieve()` walks entries by `(hash, collision differentiator)`, prefetching the whole object at iteration start when enabled and appropriate.
- `fzap_get_stats()` gathers header, pointer-table, and leaf histograms.

## Important Details
- `zap_iterate_prefetch` defaults on and is intended for mostly-full iterations; callers can disable via cursor init variants in `zap_micro.c`.
- Pointer-table growth is deliberately incremental to avoid large synchronous copy spikes.
- Hash table growth is capped before using all hash bits, returning `ENOSPC` in aberrant cases.
- Corrupt ZAP header/leaf type checks in `zap_deref_leaf()` return `EIO` rather than proceeding.
