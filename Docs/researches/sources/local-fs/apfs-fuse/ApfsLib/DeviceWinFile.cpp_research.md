# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceWinFile.cpp

This Windows-only implementation reads a regular file via `std::ifstream`.

`Open()` opens the file in binary mode, seeks to end to determine size, then rewinds. `Close()` closes the stream. `Read()` seeks to the requested offset and reads the requested length.

Notable risk: `Read()` always returns true and has a TODO for error handling, so short reads or stream failures are not reported to callers.

It is selected as the default fallback by `Device::OpenDevice()` on Windows when the path is not a physical drive or recognized image type.
