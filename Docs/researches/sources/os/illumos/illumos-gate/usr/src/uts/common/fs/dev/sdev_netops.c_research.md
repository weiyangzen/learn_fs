# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_netops.c

This file implements vnode overrides for `/dev/net`, where entries represent active network datalinks using vanity names.

Key routines:
- `devnet_validate()` checks that a cached node still corresponds to a current datalink and that non-global-zone access is allowed by `zone_check_datalink()`.
- `devnet_create_rvp()` opens a datalink via `dls_devnet_open()`, obtains its device number, and prepares character-device attributes.
- `devnet_lookup()` handles `.`, `..`, cache lookup, stale attribute refresh, dynamic creation, and stores a `dls_dl_handle_t` in `sdev_private` while the node is active.
- `devnet_filldir_datalink()` creates or refreshes cache entries while walking datalinks.
- `devnet_filldir()` prunes invalid ready nodes, then enumerates global or zone-visible datalinks depending on mount context.
- `devnet_readdir()` fills on offset zero and delegates output to `devname_readdir_func()`.
- `devnet_inactive_callback()` closes the held datalink handle and marks attributes invalid.
- `devnet_inactive()` delegates common inactive handling to `devname_inactive_func()`.

The vnode table overrides lookup, readdir, and inactive, and rejects mutation operations.

Important dependencies include DLS management APIs, zone datalink walking, sdev node/cache helpers, and spec vnode conversion through `sdev_to_vp()`.

Risk areas include keeping `sdev_private` handle lifetime balanced, refreshing stale device numbers after detach/reattach, and matching global-zone versus non-global-zone visibility rules.
