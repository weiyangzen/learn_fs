# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ptsops.c

This file implements vnode overrides for `/dev/pts`, where entries represent allocated pseudo-terminal subsidiary devices.

Key routines:
- `devpts_getvnodeops()` returns the global `/dev/pts` vnodeops pointer.
- `devpts_strtol()` safely parses a numeric minor name and rejects malformed names such as `4foo` or negative values.
- `devpts_validate()` checks that the pts driver is attached, the minor is valid for the current zone, and cached uid/gid attributes match PTMS ownership.
- `devpts_create_rvp()` builds character-device attributes for a valid pty minor and zone.
- `devpts_prunedir()` validates ready children and removes invalid/stale unreferenced nodes.
- `devpts_lookup()` delegates dynamic creation to `devname_lookup_func()` and asserts that sdev nodes do not expose a realvp in a way that would break namefs fattach protections.
- `devpts_create()` allows open/create semantics to find existing nodes but rejects creation of missing nodes with `EROFS`.
- `devpts_readdir()` prunes on first offset and delegates formatting to `devname_readdir_func()`.
- `devpts_set_id()` updates PTMS owner state when uid/gid changes.
- `devpts_setattr()` uses common `devname_setattr_func()` with uid/gid callback protocol.

The vnode table overrides lookup, create, readdir, and setattr, while rejecting remove/mkdir/rmdir/symlink/security-attribute operations.

Important dependencies are PTMS APIs, sdev validators, common lookup/readdir/setattr helpers, and namefs behavior around fattach.

Risk areas include pty minor reuse, zone ownership validation, and the documented security assumption that `VOP_REALVP()` on the sdev node returns `ENOSYS`.
