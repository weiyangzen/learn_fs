# File Research: sources/os/linux/linux-stable/fs/isofs/Kconfig

Defines ISO 9660 filesystem configuration.

Options:
- `ISO9660_FS`: tristate CD-ROM filesystem support, selects `BUFFER_HEAD`, builds as `isofs`.
- `JOLIET`: optional Microsoft Joliet Unicode filename extension, depends on ISOFS and selects `NLS`.
- `ZISOFS`: optional transparent compressed-file extension, depends on ISOFS and selects `ZLIB_INFLATE`.

The help text describes Rock Ridge support as part of the base ISOFS driver and Joliet/zisofs as optional extensions.
