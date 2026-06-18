# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_page.c

Implements low-level hash page manipulation, bucket splitting, overflow allocation, bitmap management, and disk page I/O. `putpair` appends a regular key/data pair into a page. `__delpair` removes a pair, compacts data and offset entries, and delegates large-pair deletion when needed.

`__split_page` redistributes records from an old bucket to a new bucket during linear-hash expansion. If it encounters overflow or big-pair structure, `ugly_split` handles mixed regular/large entries and allocates overflow pages for either destination. `__addel` inserts a pair into a bucket chain, using `squeeze_key`, overflow pages, or `__big_insert`, then expands the table when fill factor is exceeded.

`__add_ovflpage` allocates and links an overflow page. `__get_page` and `__put_page` translate bucket/overflow addresses to file pages, initialize new pages, and perform byte swapping for non-native byte order. `__ibitmap`, `overflow_page`, `__free_ovflpage`, and `fetch_bitmap` manage overflow-page bitmap allocation and reclamation.

Dependencies include `hash_buf.c`, `hash_bigkey.c`, page macros from `page.h`, address macros from `hash.h`, and `__dbtemp`.

Risks/invariants: page offsets are 16-bit and depend on `HASH_BSIZE`. Overflow exhaustion writes a diagnostic to stderr and returns `EFBIG`. The split path is complex and historically fragile.
