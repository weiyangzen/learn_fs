# File Research: sources/os/linux/linux/fs/ecryptfs/Kconfig

## Role

`fs/ecryptfs/Kconfig` defines build configuration options for the eCryptfs filesystem layer.

## Options

`ECRYPT_FS` is a tristate option for eCryptfs. It depends on keys and crypto support, and on encrypted keys being available or disabled. It selects ECB, CBC, MD5 crypto support, and notes that userspace components are required.

`ECRYPT_FS_MESSAGING` is a bool depending on `ECRYPT_FS`. It enables `/dev/ecryptfs` notifications for userspace key wrap/unwrap operations, including OpenSSL-backed handling.

## Research Notes

Read completely. This file controls feature availability; implementation files are outside this group.
