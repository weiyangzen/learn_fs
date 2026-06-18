# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceMac.cpp

This macOS-only implementation opens files/devices read-only and determines size by `stat` for regular files or `DKIOCGETBLOCKCOUNT`/`DKIOCGETBLOCKSIZE` for block/character devices.

Reads are performed with `pread`. `Close()` closes the descriptor and resets state; destructor calls `Close()`.

It prints some device mode and geometry information unconditionally, plus optional debug open info.

Notable risk: like the Linux version, `Read()` stores `pread()` return in `size_t`, which is not ideal for error handling. It also does not check ioctl return codes before computing size.
