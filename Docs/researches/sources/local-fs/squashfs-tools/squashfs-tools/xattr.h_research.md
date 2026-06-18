# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr.h

Shared xattr data model and API declarations for both `mksquashfs` and `unsquashfs`.

Defines:
- Squashfs xattr flags/prefix masks and inline/out-of-line size policy constants.
- Format-prefix constants for base64, binary, hex, and escaped text xattr values.
- `struct xattr_list`, `struct dupl_id`, `struct prefix`, and `struct xattr_add`.

When `XATTR_SUPPORT` is enabled:
- Declares xattr table generation, reading, restoration, regex, parsing, pseudo, printing, and system write functions.
- Provides a no-op `write_xattr()` if xattr metadata support exists but OS write support is absent.

When `XATTR_SUPPORT` is disabled:
- Provides stubs that reject filesystems containing xattrs for mksquashfs append/import, return invalid xattr ids, disable printing/restoration, and report unsupported pseudo xattrs.

Also defines:
- `xattrs_supported()` and `XATTR_DEF` according to build-time xattr support, OS support, and default policy.
