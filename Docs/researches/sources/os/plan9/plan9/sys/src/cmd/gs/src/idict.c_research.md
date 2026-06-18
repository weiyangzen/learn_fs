# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.c

Implements Ghostscript dictionaries. Dictionaries have separate key and value arrays, packed or unpacked key representation, open-addressing lookup, deleted-entry markers, save/restore integration, and dictionary-stack cache updates.

Core behavior:
- `dict_alloc` creates dictionary object and contents.
- `dict_create_contents` allocates value array and packed/unpacked key array with wraparound/deleted sentinel.
- `dict_find` hashes names, strings converted to names, integers, reals, and fallback object types; packed dictionaries use macro-generated probing.
- `dict_put` performs store checks, auto-expands if configured, converts string keys to names, unpacks if packed representation cannot hold key, updates count and name single-definition cache.
- `dict_undef` removes entries, marks deleted/empty slots, clears name cache, and nulls value.
- `dict_copy_entries`, `dict_resize`, and `dict_grow` preserve name-cache and save/restore invariants.
- Enumeration APIs: `dict_first`, `dict_next`, `dict_value_index`, `dict_index_entry`.

Design coupling is explicit: dictionaries must update dictionary-stack cached top values and name cached-value pointers, so they depend on `iddstack.h`.
