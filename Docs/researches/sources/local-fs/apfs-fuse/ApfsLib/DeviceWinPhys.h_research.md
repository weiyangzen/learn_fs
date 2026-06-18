# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.h

This Windows-only header declares `DeviceWinPhys`, a `Device` backed by a Win32 `HANDLE` to a physical disk.

It exposes open, close, read, and size methods. Private state is the drive handle and byte size.

The header includes `Windows.h` and `tchar.h`, guarded by `_WIN32`.

It supports read-only raw disk access for Windows APFS containers and Fusion components.
