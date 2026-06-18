# sources/sync-backup/borg/src/borg/helpers/lrucache.py

## Purpose
Provides a small mutable mapping with least-recently-used eviction and disposal callbacks, used by FUSE metadata/data caches and other bounded caches.

## Important APIs, Types, And Functions
`LRUCache[K, V]` implements `MutableMapping` methods `__setitem__`, `__getitem__`, `__delitem__`, `__contains__`, `__len__`, `__iter__`, plus `replace`, `clear`, `keys`, `values`, and `items`.

## Control Flow
The internal `OrderedDict` tracks recency. `__getitem__` moves a key to the end before returning. `__setitem__` asserts the key is new, evicts from the front while at capacity, calls `dispose` for each evicted value, then appends. `replace` updates an existing key without disposal and without changing the assertion model. `clear` disposes all values.

## State And Persistence
State is in-memory: `_cache`, `_capacity`, and `_dispose`. It does not persist anything.

## Dependencies And Integration Points
Used by `fuse.py` and `hlfuse.py` for open-file item/chunk caches. The disposal hook allows callers to close resources or release external state when entries are removed.

## Risks And Edge Cases
Capacity zero would make `__setitem__` loop attempt to pop from an empty dict. Replacement must use `replace` or delete first; otherwise assertions fire. `replace` does not move entries to most-recent. `items()` returns the live view, so iteration while mutating has normal mapping risks.

## Test Signals
Existing tests should verify eviction order, disposal on eviction/delete/clear, `__getitem__` recency updates, assertions for duplicate set and missing replace, and behavior of mapping views.
