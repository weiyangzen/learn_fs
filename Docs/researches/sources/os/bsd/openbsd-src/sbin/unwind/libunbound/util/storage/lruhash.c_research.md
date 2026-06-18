# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.c

Implements a locked hash table with overflow chains, an LRU list, memory accounting, resizing, and eviction.

Core lifecycle:
- `lruhash_create` allocates the table, initializes the table lock, callback functions, bin array, and per-bin locks.
- `lruhash_delete` destroys locks and deletes entries through callback functions.
- `lruhash_clear` removes all entries while respecting bin and entry locks.

Lookup and mutation:
- `lruhash_insert` inserts a new entry or updates an existing entry’s data. Existing-key updates delete the new key and old data, then store the new data.
- `lruhash_lookup` locks the table and bin, finds the entry, touches it to the front of the LRU list, then obtains a read or write lock on the entry before releasing the bin.
- `lruhash_remove` unlinks an entry from bin and LRU structures, optionally marks it pending deletion, and calls delete callbacks after releasing table/bin locks.
- `lruhash_insert_or_retrieve` is getdns-specific: it returns a write-locked existing entry if present, otherwise inserts and write-locks the supplied entry.

Eviction and growth:
- `reclaim_space` removes LRU-end entries until memory is within `space_max`, keeping the MRU entry so the table is not emptied by reclaim.
- Reclaimed entries are put on a temporary list and freed outside the main critical section.
- `table_grow` doubles the bin array when `num >= size`, moves overflow chains using the new mask, then destroys old bin locks.
- `lruhash_update_space_used` and `lruhash_update_space_max` adjust accounting and may trigger eviction.

Diagnostics and traversal:
- `lruhash_status` logs entry count, memory use, array size, and optional per-bin collision stats.
- `lruhash_get_mem` includes table, bins, entry-accounted memory, and lock overhead.
- `lruhash_traverse` locks the table and each bin, locks each entry, invokes a callback, then unlocks.

Important invariants:
- Table lock protects lookup array, LRU list, size, memory counters, and growth.
- Bin locks protect overflow chains.
- Entry rwlocks protect entry contents, not hash/key/LRU/overflow links.
- Function pointers are checked with `fptr_wlist` before callback use.
