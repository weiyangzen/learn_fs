# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.h

This header declares orphanage and adoption support for online repair.

When `CONFIG_XFS_ONLINE_REPAIR` is enabled, it exposes:
- orphanage creation and release,
- orphanage IOLOCK/ILOCK helpers,
- adoption eligibility,
- adoption transaction allocation,
- adoption name computation,
- adoption move,
- adoption transaction rolling.

`xrep_orphanage_try_create` is an important wrapper: during repair it attempts to create/attach the orphanage, but treats `ENOENT`, `ENOTDIR`, and `ENOSPC` as nonfatal. This lets scrub continue even if later orphan adoption will be impossible.

`struct xrep_adoption` stores:
- scrub context,
- chosen orphanage name,
- parent pointer update args,
- block reservations for orphanage and child,
- whether to bump the child link count.

Without online repair, `struct xrep_adoption` is an empty stub and `xrep_orphanage_rele` compiles to a no-op.
