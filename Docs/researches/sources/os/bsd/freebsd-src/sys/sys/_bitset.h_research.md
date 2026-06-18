# File Research: sources/os/bsd/freebsd-src/sys/sys/_bitset.h

Base bitset type-definition macros.

Defines:
- `_BITSET_BITS` as bits per `unsigned long`.
- `__howmany()`, `__bitset_words()`.
- `__BITSET_DEFINE(type, size)` producing a struct with an `unsigned long __bits[]` array sized for the requested bit count.
- `__BITSET_DEFINE_VAR()` workaround for variable-size declarations.
- Under `_KERNEL` or `_WANT_FREEBSD_BITSET`, defines a default `struct bitset` and public `BITSET_DEFINE` wrappers.

Research relevance:
- Common substrate for CPU/domain sets and other kernel bit-vector types.
