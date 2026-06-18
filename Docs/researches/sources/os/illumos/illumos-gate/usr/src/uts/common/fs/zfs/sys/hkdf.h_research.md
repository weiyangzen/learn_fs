# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/hkdf.h

Read status: complete, 29 lines.

Purpose: declares HKDF-SHA512 key derivation helper.

Key API:
- `hkdf_sha512()` derives an output key from key material, salt, info, and requested output length.

Dependencies: `sys/types.h`.

Research notes:
- Used by encryption/key derivation code paths.
- Header is intentionally minimal and does not expose implementation details.
