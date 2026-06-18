# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.h

`iter_hints.h` declares the iterator hint subsystem API. `struct iter_hints` contains an RW lock and a `name_tree` of hint entries sorted by class and DNS name so closest-enclosing ancestor lookups work for root and stub hints.

`struct iter_hints_stub` stores the tree node, owned `delegpt`, and `noprime` flag. The public API covers create/delete, config application, root and closest hint lookup, stub priming lookup, memory accounting, externally adding/removing stubs, root-class iteration, and tree swapping.

The header documents the locking contract carefully: callers may pass `nolock` when they already hold the lock, while successful non-`nolock` lookups may require the caller to release the read lock.
