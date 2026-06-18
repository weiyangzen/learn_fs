# sources/user-network-fs/davfs2/etc/meson.build

## Purpose
This Meson build fragment installs davfs2 system configuration templates, secrets placeholders, certificate directories, and shared template copies.

## Important APIs and targets
It calls `install_data` for `secrets` with `install_mode : 'rw-------'`, installs `davfs2.conf` into `davfs2_sysconfdir`, installs certificate directories using either `install_emptydir` for Meson >= 0.60.0 or `install_subdir` fallback for older Meson, and installs `davfs2.conf` plus `secrets` into `davfs2_sharedir`.

## Control flow
The only branch is the Meson version check. Newer Meson creates empty directories directly; older Meson copies checked-in directory placeholders.

## State and persistence behavior
At install time it creates or copies persistent configuration and certificate storage locations. The secrets file mode is security-sensitive.

## Dependencies and integration points
It depends on top-level Meson variables such as `davfs2_sysconfdir`, `davfs2_certdir`, and `davfs2_sharedir`. It connects source templates under `etc/` to runtime lookup paths documented in the manpages.

## Risks
Fallback `install_subdir('private', install_dir : davfs2_sysconfdir / davfs2_certdir)` relies on source directory shape and may copy contents rather than only creating empty directories. Directory permissions for cert/private directories are not explicitly set in the new `install_emptydir` path. Any mismatch with runtime expectations can break certificate or secret lookup.

## Test signals
Run `meson install --destdir` and assert installed file paths and modes, especially `secrets` mode and certificate/private directory existence. Test both Meson version paths if compatibility is still intended.
