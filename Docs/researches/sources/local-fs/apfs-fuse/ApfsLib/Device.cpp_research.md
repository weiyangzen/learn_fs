# File Research: sources/local-fs/apfs-fuse/ApfsLib/Device.cpp

This file implements the abstract `Device` base constructor/destructor and the `Device::OpenDevice()` factory.

The factory recognizes Windows physical drive names, `.dmg` files, `.sparseimage` files, then falls back to platform-specific regular device/file implementations: `DeviceWinFile`, `DeviceLinux`, or `DeviceMac`.

`.dmg` and `.sparseimage` are opened via image-aware adapters that may understand compression/encryption. VDI support is included by header but not selected by extension in this factory.

The base constructor sets default sector size to 0x200. Returned devices are raw heap pointers; callers own deletion and closing.
