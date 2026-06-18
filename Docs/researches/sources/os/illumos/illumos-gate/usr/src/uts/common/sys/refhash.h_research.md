# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refhash.h

## Role

`refhash.h` declares a generic reference-counted hash table helper for kernel objects with embedded linkage.

## Data Model

`refhash_link_t` is embedded in client objects and contains:
- per-bucket chain link.
- global object-list link.
- flags.
- reference count.

`RHL_F_DEAD` marks a dead object.

`refhash_t` contains bucket lists, global object list, object size and embedded-offset metadata, hash/compare callbacks, and optional destructor.

## Interfaces

The API supports:
- create/destroy.
- insert/remove.
- lookup and linear search.
- hold/release.
- first/next iteration.
- object validity checking.

Callbacks are typed for hash, compare, destructor, and evaluation predicates.

## Research Notes

This header defines intrusive lifetime-managed hash infrastructure. Correct client use depends on embedding `refhash_link_t` at the registered offset and balancing holds/releases around lookup/iteration.
