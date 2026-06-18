# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.h

This header declares `DeviceVDI`, a `Device` implementation for VirtualBox VDI files.

It stores logical disk size, VDI block size/count, data offset, block map, and `FILE*`.

Public API is the standard `Device` open/close/read/size interface.

Although included by `Device.cpp`, `.vdi` extension dispatch is not implemented in `Device::OpenDevice()` in the read file set.
