# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/page.h

Documents and defines the hash page layout. A page begins with a uint16_t offset table: count, alternating key/data offsets, free-space amount, and free-area pointer. Data grows downward from the end of the page while offset metadata grows upward.

Macros compute pair size, big-pair overhead, overflow marker size, free space, current data offset, metadata size, and whether a regular pair fits while still leaving room for a future overflow marker. `SPLIT_RETURN` carries page pointers and continuation addresses for complex split handling involving big key/data chains.

Dependencies: included with `hash.h`; uses `DBT` and `BUFHEAD`.

Risks/invariants: all offsets fit in `uint16_t`, so hash bucket size constraints are central. `PAIRFITS` intentionally requires extra room for an overflow pointer to avoid later impossible split states.
