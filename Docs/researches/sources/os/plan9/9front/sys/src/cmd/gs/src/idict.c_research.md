# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.c

Implements Ghostscript’s interpreter dictionary hash table.

Key behavior:
- Defines maximum dictionary size from `max_array_size - 1` and defaults dictionaries to packed keys.
- Rounds dictionary storage size directly on small-memory systems and to powers of two on larger systems unless huge.
- `dict_alloc` creates the dictionary object as refs, stores allocator as foreign struct, and initializes contents.
- Dictionary contents use separate values and keys arrays; keys may be packed shortarray entries or full refs.
- Packed dictionaries use sentinel empty/deleted keys and a wraparound slot.
- `dict_unpack` converts packed keys to full refs when required by unsupported key forms or large name indexes.
- `dict_find` hashes names/strings/integers/reals/other refs, searches packed or unpacked tables with open addressing, returns existing value slot or insertion slot, and reports `dictfull`.
- Strings are converted to names for lookup/insert when readable.
- `dict_put` performs store checks, auto-grows when configured, inserts new keys, updates count, updates single-definition name caches when allowed, and stores values with save tracking.
- `dict_undef` removes entries, marks deleted/empty slots, decrements count, clears name caches, and nulls values.
- Provides length, maxlength, max-index, copy, resize, grow, enumeration, value-index, and index-entry operations.
- Resize rebuilds contents, copies entries, preserves/updates name caches, frees or save-records old arrays, and refreshes dictionary-stack top cache.

Research notes:
- The implementation is tightly coupled to save/restore, GC relocation, name cache optimization, and dictionary-stack caches.
- Packed-name keys are a major fast path, but arbitrary keys force unpacking.
