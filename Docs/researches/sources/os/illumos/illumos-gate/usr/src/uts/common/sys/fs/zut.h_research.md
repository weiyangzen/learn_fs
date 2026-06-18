# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zut.h

## Role

Defines the ioctl ABI for the ZFS unit test driver `/dev/zut`.

## Key Definitions

- Driver/device names: `ZUT_DRIVER` and `ZUT_DEV`.
- Version string: `ZUT_VERSION_STRING`.
- Ioctl base: `ZUT_IOC`.
- Request flags:
  - `ZUT_IGNORECASE`
  - `ZUT_ACCFILTER`
  - `ZUT_XATTR`
  - `ZUT_EXTRDDIR`
  - `ZUT_GETSTAT`

## Ioctl Payloads

- `zut_lookup_t` carries lookup request flags, directory/file/xattr file names, output directory-entry flags, return code, real resolved path, extended attribute bits, and `stat64`.
- `zut_readdir_t` carries an output-buffer pointer as `uint64_t`, output logical offset, directory/file names, request flags, return code, EOF marker, returned bytes, and buffer length.
- `zut_ioc_t` enumerates lookup and readdir commands.

## Risk Notes

This is test-driver ABI rather than filesystem core, but structure layout matters for ioctl callers, especially pointer-sized fields represented as fixed-width integers.
