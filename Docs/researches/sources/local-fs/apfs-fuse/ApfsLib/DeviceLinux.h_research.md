# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.h

This Linux-only header declares `DeviceLinux`, a `Device` backed by a POSIX file descriptor.

It exposes standard open/close/read/size methods and stores `int m_device` plus `uint64_t m_size`.

Compilation is guarded by `#ifdef __linux__`.

It is the default fallback device implementation selected by `Device::OpenDevice()` on Linux.
