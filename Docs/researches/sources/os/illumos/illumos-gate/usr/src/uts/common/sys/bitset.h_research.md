# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitset.h

`bitset.h` wraps bitmap storage in `bitset_t`, with fields for backing words, capacity in words, and fanout. It is available to `_KERNEL`, `_FAKE_KERNEL`, and `_KMEMUSER` consumers.

The API covers lifecycle (`bitset_init`, `bitset_init_fanout`, `bitset_fini`), resizing/capacity, normal and atomic add/delete/test operations, membership/null/find queries, boolean computations (`and`, `or`, `xor`), zero/copy/match helpers. It depends on `bitmap.h` for bit-level representation.
