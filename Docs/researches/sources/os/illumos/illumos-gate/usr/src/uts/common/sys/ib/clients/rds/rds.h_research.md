# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds.h

This legacy RDS socket/STREAMS header defines the main socket-side RDS state and bind fanout interfaces.

Core definitions:
- `rds_t` stores reference synchronization, TPI state, flags, socket family, credentials, bound port/source address, upper-layer private data, bind-hash linkage, port quota, and zone ID.
- `RDS_CLOSING` marks close state.
- Refcount macros increment/decrement under `rds_lock`; final decrement calls `rds_free()`.
- Bind fanout entries contain an RDS chain head and lock, padded for cache layout.
- Bind hash is based on network-order local port and a power-of-two fanout size.
- `AF_INET_OFFLOAD` is defined as `30`.

API surface:
- Hash init, create/free, bind hash insert/remove/fanout lookup, message delivery entry point, bind-address/local-interface checks, and module init/fini.

Risk-sensitive invariants:
- Refcount macro frees while holding `rds_lock`, so `rds_free()` must match that expectation.
- Bind fanout and port quota are zone-aware.
- This is socket-facing RDS, separate from the IB transport implementation.
