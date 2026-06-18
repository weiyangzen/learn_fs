# File Research: sources/os/linux/linux/fs/isofs/Kconfig

Defines ISO9660 filesystem configuration.

Options:
- `ISO9660_FS`: tristate ISO 9660 CD-ROM filesystem support; selects `BUFFER_HEAD`; module name is `isofs`.
- `JOLIET`: optional Microsoft Joliet Unicode extension support; depends on ISO9660 and selects `NLS`.
- `ZISOFS`: optional transparent decompression extension; depends on ISO9660 and selects `ZLIB_INFLATE`.

The help text documents Rock Ridge support as part of the driver and points to ISOFS documentation/CD-ROM HOWTO material.
