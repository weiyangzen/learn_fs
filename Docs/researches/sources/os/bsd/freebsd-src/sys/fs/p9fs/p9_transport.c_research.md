# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.c

This file implements the registry for p9fs transport modules.

Key behavior:
- Maintains a global `TAILQ` of `struct p9_trans_module` entries.
- Initializes the list at `SYSINIT` time with subsystem `SI_SUB_DRIVERS`.
- `p9_register_trans()` appends a transport module.
- `p9_unregister_trans()` removes a transport module.
- `p9_get_trans_by_name()` linearly searches by transport name and returns the matching module or `NULL`.

Research-relevant notes:
- No explicit locking protects the transport list; registration is expected to occur during controlled driver/module lifecycle.
- The default client path expects a transport named `"virtio"` unless the mount specifies `trans=`.
