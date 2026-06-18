# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.h

Header for iterator do-not-query address storage.

Core structure:
- `struct iter_donotq`: regional allocator plus address-span RB tree.

API:
- create/delete.
- apply config.
- lookup blocked address.
- memory accounting.

Role in group:
- Interface used by iterator code to quickly reject upstream target addresses that must not be queried.
