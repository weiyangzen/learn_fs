# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_func.c

Provides the default hash function pointer for DB hash tables. Historical alternative hash functions are retained inside `#if 0`; the active default is `hash4`, attributed to Chris Torek.

`hash4` consumes the key bytes in an unrolled eight-byte loop, applying the `h = h * 33 + byte` variant (`HASH4b`) and returning a 32-bit hash. `__default_hash` is initialized to `hash4` and is used unless callers supply `HASHINFO.hash`.

Dependencies: included by the hash build and declared through `hash/extern.h`.

Risks/invariants: existing on-disk hash files store `H_CHARKEY`, the hash of a fixed string, so changing the default hash breaks compatibility unless a matching custom hash is supplied at open time.
