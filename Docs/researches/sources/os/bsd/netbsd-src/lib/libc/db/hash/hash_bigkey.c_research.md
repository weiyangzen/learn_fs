# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_bigkey.c

Handles hash key/data pairs too large to fit as ordinary page entries. `__big_insert` writes key bytes across partial-key overflow pages, then writes data across full-key/full-key-data pages, preserving the invariant that complete data on a page leaves detectable free space.

`__big_delete` frees all overflow pages belonging to a large pair except the first page, which is rewritten to point to the following chain. `__find_bigpair` compares a candidate large key across overflow pages. `__find_last_page` locates the last page in a large pair and returns any following overflow page address.

`__big_return` materializes a large value into `hashp->tmp_buf`, using `collect_data` recursively. `__big_keydata` materializes both key and data using `collect_key` and `__big_return`, used by sequential scans and bucket splits. `__big_split` relocates a large pair during linear-hash bucket splitting, reconnecting the pair to either the old or new bucket and preserving following overflow chains.

Dependencies: uses `__get_buf`, `__add_ovflpage`, `__free_ovflpage`, `__call_hash`, and hash page markers from `hash.h`.

Risks/invariants: recursive collection assumes enough buffers remain resident; it checks saved buffer addresses and reports `EINVAL` for buffer exhaustion. Large-pair deletion and split are subtle because page links double as both continuation and bucket overflow links.
