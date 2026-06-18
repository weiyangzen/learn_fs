# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.h

This macOS-only header declares `DeviceMac`, a `Device` backed by a POSIX file descriptor and macOS disk ioctls.

It exposes open, close, read, and size methods, and stores descriptor plus byte size.

Compilation is guarded by `#ifdef __APPLE__`.

It is selected by `Device::OpenDevice()` as the fallback device implementation on macOS.
