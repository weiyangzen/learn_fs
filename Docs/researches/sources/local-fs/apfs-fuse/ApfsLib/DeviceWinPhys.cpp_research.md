# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinPhys.cpp

This Windows-only implementation reads physical drives using Win32 APIs. `Open()` converts the UTF-8 path to wide chars, opens it with `CreateFile`, queries `IOCTL_DISK_GET_DRIVE_GEOMETRY_EX`, and stores disk size.

`Read()` seeks with `SetFilePointerEx` and reads with `ReadFile`. `Close()` closes the handle and resets state.

It is selected by `Device::OpenDevice()` for paths beginning with `\\.\PhysicalDrive`.

Notable risks: `Read()` returns only the `ReadFile` boolean and does not verify `read_bytes == len`. `Open()` does not close the handle if geometry query fails with zero bytes returned.
