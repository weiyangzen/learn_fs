# File Research: sources/windows/reactos/drivers/filesystems/msfs/fsctrl.c

This file provides `MsfsFileSystemControl`, the MSFS filesystem-control dispatcher.

The implementation obtains the file object and FCB for logging, switches on `FsControlCode`, and currently returns `STATUS_NOT_IMPLEMENTED` for every code.

Research notes:
- This is a placeholder dispatch path.
- It still completes the IRP consistently with status and zero information.
- No MSFS-specific FSCTLs are implemented here.
