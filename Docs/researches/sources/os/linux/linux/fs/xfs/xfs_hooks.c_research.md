# File Research: sources/os/linux/linux/fs/xfs/xfs_hooks.c

Implements the small live-hook wrapper around Linux blocking notifier chains for optional XFS hook points.

Key elements:
- `xfs_hooks_init` initializes a blocking notifier head.
- `xfs_hooks_add` registers a hook after asserting a callback is installed and that `struct xfs_hook.nb` is first in the structure.
- `xfs_hooks_del` unregisters a hook.
- `xfs_hooks_call` invokes the chain and returns the final notifier result.

Dependencies:
- Depends on notifier-chain infrastructure and `CONFIG_XFS_LIVE_HOOKS` declarations from `xfs_hooks.h`.
- Includes core XFS headers for consistency and tracing/assertion support.

Research notes:
- The implementation is intentionally thin; static-key enable/disable behavior lives in the header macros used by hook call sites.
