# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.h

This header declares `DeviceDMG`, a `Device` implementation for DMG files.

Internal `DmgSection` stores compression method, comment, logical disk offset/length, source DMG offset/length, and optional per-section cache. The class stores `DiskImageFile`, logical size, data-fork offset, raw-image flag, CRC helper, section vector, optional debug stream, and optional global cache.

Public methods implement the standard `Device` interface: open, close, read, and size.

Private methods parse XML plist headers, resource-fork headers, and `mish` block maps. Resource-fork parsing is declared but not implemented in the `.cpp`.
