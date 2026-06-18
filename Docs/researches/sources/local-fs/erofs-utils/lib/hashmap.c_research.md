# File Research: sources/local-fs/erofs-utils/lib/hashmap.c

## Purpose
Generic chained hashmap implementation copied from Git, plus hash helpers and a memory interning pool.

## Hash Helpers
- `strhash()`: FNV-1 32-bit hash over NUL-terminated string.
- `strihash()`: case-insensitive ASCII variant.
- `memhash()`: FNV-1 over arbitrary bytes.
- `memihash()`: case-insensitive ASCII byte variant.

## Hashmap Functions
- `hashmap_init()`: allocates table sized to requested initial size and load factor.
- `hashmap_free()`: frees table only if map is empty, otherwise returns `-EBUSY`.
- `hashmap_get()` / `hashmap_get_next()`: lookup first/next equal entry.
- `hashmap_add()`: inserts and grows table past load threshold.
- `hashmap_remove()`: removes an entry and shrinks table below threshold.
- `hashmap_iter_init()` / `hashmap_iter_next()`: table iteration.

## Interning
- `memintern()`: stores immutable byte strings in a static hashmap and returns a stable interned pointer.

## Interactions
- Used by blob chunk dedupe and other map-based helpers.
- Requires caller entries to embed `struct hashmap_entry`.

## Notes
The table grows/shrinks by a factor of 4 and defaults to an equality callback that treats same-hash entries as equal.
