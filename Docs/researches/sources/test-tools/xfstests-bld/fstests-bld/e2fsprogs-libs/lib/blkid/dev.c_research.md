# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/dev.c

Purpose: manages blkid device object allocation/freeing and public device iteration.

Important APIs and control flow: `blkid_new_dev()` calloc-allocates a device and initializes its list heads. `blkid_free_dev(dev)` removes it from the cache device list, frees all attached tags through `blkid_free_tag`, frees the name, and releases the struct. `blkid_dev_devname(dev)` returns `bid_name`. Iterator APIs allocate a magic-checked iterator, optionally install copied tag search criteria, walk `cache->bic_devs`, filter through `blkid_dev_has_tag`, and free iterator state at end.

State and persistence: device objects are intrusive-list members owned by a cache. Iterators hold traversal position and optional copied search strings.

Dependencies and integration: depends on `blkidP.h`, `list.h`, and tag APIs. Test program exercises iteration and search.

Risks and test signals: `blkid_dev_iterate_end` leaks `search_type` and `search_value`; iteration is invalid if cache mutates concurrently. Test allocation/free, filtered iteration, iterator misuse magic checks, and debug dumps.
