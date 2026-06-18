# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/extern.h

Declares private hash implementation functions shared across the hash source files. The declarations cover overflow-page allocation/free, key/data insertion and deletion, large-key handling, buffer cache lifecycle, hashing, page I/O, bitmap allocation, table expansion, and bucket splitting.

It also declares `__default_hash`, the default hash function pointer provided by `hash_func.c`, plus optional hash statistics counters.

Dependencies: included after `hash.h` and `page.h`, which define `HTAB`, `BUFHEAD`, `SPLIT_RETURN`, and page-format constants.

Risks/invariants: no include guard is present in this file; it relies on conventional include ordering. Most prototypes expose mutable `HTAB *` state and raw page buffers, so callers must maintain buffer pinning and page-format invariants.
