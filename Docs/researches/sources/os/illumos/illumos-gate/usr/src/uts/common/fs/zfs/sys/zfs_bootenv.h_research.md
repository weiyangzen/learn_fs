# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_bootenv.h

Defines string keys used in ZFS label boot-environment nvlists.

Key elements:
- Vendor prefixes: `illumos`, `freebsd`, and `grub`.
- Bootonce and bootonce-used keys for FreeBSD and illumos.
- NV store keys for FreeBSD and illumos.
- `BOOTENV_OS` selects illumos as the local OS namespace.
- `OS_BOOTONCE`, `OS_BOOTONCE_USED`, and `OS_NVSTORE` alias the active OS namespace.

Main dependencies and interactions:
- No subsystem dependencies beyond C++ linkage guards.
- Used wherever ZFS labels store or retrieve boot environment metadata.

Implementation notes:
- This is a shared key contract. Compatibility depends on stable strings, not binary structure layout.
