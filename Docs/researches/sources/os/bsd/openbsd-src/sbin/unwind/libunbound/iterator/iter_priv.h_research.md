# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.h

`iter_priv.h` declares the iterator private-address filtering state and API. `struct iter_priv` owns a regional allocator, an address tree for blocked address spans, and a name tree for private-domain exceptions.

The exported functions create/delete the structure, apply config, test and sanitize RRsets, and report memory use. `priv_rrset_bad()` is the key runtime entry point: it may mutate a parsed RRset by removing individual bad RRs and returns whether the entire RRset should be dropped.

The header is intentionally narrow and hides the address/name lookup helpers inside `iter_priv.c`.
