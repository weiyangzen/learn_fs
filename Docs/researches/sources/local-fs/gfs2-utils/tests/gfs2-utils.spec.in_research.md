# File Research: sources/local-fs/gfs2-utils/tests/gfs2-utils.spec.in

RPM spec template used only for testing, not distro packaging.

Defines package metadata for `gfs2-utils`, build dependencies, source URL, configure/build/install steps, and file list.

Notable behavior:
- Installs only the `gfs2` subtree into buildroot.
- Removes installed `gfs2_trace` and `gfs2_lockcapture`.
- Includes utilities such as `fsck.gfs2`, `gfs2_grow`, `gfs2_jadd`, `mkfs.gfs2`, `gfs2_edit`, `tunegfs2`, `glocktop`, `gfs2_withdraw_helper`, man pages, and udev rule.

Research notes:
- `%global source_date_epoch_from_changelog 0` disables changelog requirement for source date epoch.
