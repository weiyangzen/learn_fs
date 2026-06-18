# File Research: sources/os/linux/linux-stable/fs/smb/Kconfig

## Purpose

Top-level SMB filesystem Kconfig file that includes SMB client, server, and SMB Direct configuration and defines shared SMBFS and SMB KUnit test configuration symbols.

## Main Contents

- Sources:
  - `fs/smb/client/Kconfig`
  - `fs/smb/server/Kconfig`
  - `fs/smb/smbdirect/Kconfig`
- Defines `SMBFS` as an internal tristate enabled when either the CIFS client or SMB server is built in or as a module.
- Defines `SMB_KUNIT_TESTS`, depending on `SMBFS && KUNIT`, defaulting to `KUNIT_ALL_TESTS`.

## Integration Notes

- `SMBFS` is used by the top-level SMB Makefile to include common SMB code.
- `SMB_KUNIT_TESTS` gates shared SMB KUnit test builds and is further consumed by client-specific tests.
