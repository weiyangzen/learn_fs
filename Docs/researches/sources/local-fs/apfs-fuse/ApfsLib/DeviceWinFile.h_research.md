# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.h

This Windows-only header declares `DeviceWinFile`, a `Device` backed by `std::ifstream`.

It stores the input stream and byte size, and implements open, close, read, and size.

Compilation is guarded by `_WIN32`.

The class is simple regular-file support for Windows APFS image use.
