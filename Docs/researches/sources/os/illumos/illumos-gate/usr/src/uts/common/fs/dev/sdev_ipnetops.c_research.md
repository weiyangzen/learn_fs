# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ipnetops.c

This file implements vnode overrides for the dynamic `/dev/ipnet` directory. Entries represent IP network interfaces known to the `ipnet` module and are scoped by the current zone.

Key routines:
- `devipnet_fill_vattr()` builds character-device attributes with mode `0666`, device number, and current timestamps.
- `devipnet_validate()` checks whether an existing sdev node still maps to a live `ipnet` device in the current zone and whether its minor number is current.
- `devipnet_create_rvp()` is the lookup callback used by `devname_lookup_func()` to create a node when `ipnet_if_getdev()` succeeds.
- `devipnet_lookup()` delegates dynamic creation to `devname_lookup_func()` and asserts expected real-vnode behavior for character nodes.
- `devipnet_filldir_entry()` creates missing cached entries while walking ipnet interfaces.
- `devipnet_filldir()` upgrades the directory lock, prunes invalid/stale ready nodes, and walks the current zone’s interfaces.
- `devipnet_readdir()` fills on first offset, then delegates output formatting to `devname_readdir_func()`.

The vnode operation table overrides lookup and readdir, and rejects create/remove/mkdir/rmdir/symlink/security-attribute mutation.

The main dependencies are `ipnet_if_getdev()`, `ipnet_walk_if()`, sdev cache helpers, zone ID lookup, and generic `/dev` readdir/lookup helpers.

Correctness concerns are zone scoping, stale minor detection, and avoiding deletion of nodes that still have vnode references.
