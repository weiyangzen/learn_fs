# File Research: sources/os/linux/linux-stable/fs/ecryptfs/Kconfig

## Purpose
This Kconfig file defines build options for eCryptfs.

## Options
- `ECRYPT_FS`: tristate option for the eCryptfs stacked encrypted filesystem.
  - Depends on `KEYS`, `CRYPTO`, and either `ENCRYPTED_KEYS` enabled or unavailable.
  - Selects ECB, CBC, MD5 library crypto support.
  - Builds module `ecryptfs` when selected as module.
- `ECRYPT_FS_MESSAGING`: optional bool for `/dev/ecryptfs` userspace key wrap/unwrap notifications.
  - Depends on `ECRYPT_FS`.

## Notes
The help text points to `Documentation/filesystems/ecryptfs.rst` and notes that userspace components are required.
