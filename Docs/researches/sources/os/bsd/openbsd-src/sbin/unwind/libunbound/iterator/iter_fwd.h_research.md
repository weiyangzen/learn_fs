# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.h

Header for iterator forward-zone storage.

Core structures:
- `struct iter_forwards`: RW lock and RB tree.
- `struct iter_forward_zone`: tree node, wire-format name, label count, optional forwarder delegation point, parent pointer, and class.

API:
- create/delete/apply config.
- exact and closest-encloser lookup.
- root lookup and root-class iteration.
- memory accounting.
- comparator.
- add/delete zones.
- add/delete stub holes.
- swap trees.

Role in group:
- Public contract for forward-zone policy used by the iterator and reload/config paths.
