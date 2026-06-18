# File Research: sources/os/bsd/freebsd-src/sys/sys/_domainset.h

NUMA memory-domain set type declaration.

Defines:
- In kernel builds, `DOMAINSET_SETSIZE` as `MAXMEMDOM`.
- `DOMAINSET_MAXSIZE` as 256 and default `DOMAINSET_SETSIZE` to that if not otherwise defined.
- `domainset_t` as a bitset-backed `_domainset`.
- Forward declaration `struct domainset`.
- `struct domainset_ref`, embedding a volatile policy pointer and per-object round-robin iterator.

Research relevance:
- Type substrate for NUMA domain policies and per-object domainset references.
