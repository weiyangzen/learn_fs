# sources/object-store/daos/src/vos/lru_array.c

## Purpose
Implements a generic fixed-index LRU cache/allocator backed by one or more lazily allocated subarrays. It provides allocation, lookup support through header inlines, explicit eviction, memory accounting callbacks, and aggregation of empty subarrays.

## Important APIs, Types, And Functions
Exports `lrua_array_alloc_one`, `lrua_find_free`, `lrua_evictx`, `lrua_array_alloc`, `lrua_array_free`, and `lrua_array_aggregate`. Internal callbacks wrap user `lru_callbacks` for init/fini/evict/alloc/free. `sub_find_free`, `manual_find_free`, and `array_free_one` manage circular free/LRU lists.

## Control Flow
Allocation validates power-of-two entry and subarray counts, aligns payload size, allocates the top-level array, initializes unused/free lists, then allocates the first subarray. Lookup is inline in the header. Allocation first removes an entry from a free list and inserts it as MRU; if automatic eviction is enabled and no free entry remains, it evicts the current LRU. Manual eviction mode searches subarrays with free entries or allocates an unused subarray, returning `-DER_BUSY` when capacity is exhausted.

## State And Persistence
State is in heap memory, not persistent storage. Each `lru_entry` stores key, payload pointer, and circular prev/next indexes. Each subarray tracks active LRU head, free head, payload/table pointers, and list membership. `la_evicting` prevents reentrant lookup from moving an entry while its eviction callback runs.

## Dependencies And Integration
Depends on DAOS allocation/list/assertion utilities and `vos_internal.h`. Consumers supply typed payload sizes and callbacks; header macros cast payload pointers.

## Risks
Requires `nr_ent` and `nr_arrays` powers of two and `nr_ent > nr_arrays`; these are assertions, not runtime recovery. Multi-subarray mode forces manual eviction because no global LRU exists. Key zero is invalid and marks free entries. Callback implementations must tolerate eviction/reset timing. A duplicated line appears in `lrua_lookup_idx` in the provided source and should be compile-checked.

## Test Signals
Useful tests cover allocation/free callbacks, automatic eviction order, manual eviction `-DER_BUSY`, explicit `lrua_evictx`, in-place allocation, multi-subarray aggregation, reuse-unique free ordering, and invalid stale key lookup.
