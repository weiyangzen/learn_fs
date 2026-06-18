# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfs.c

This file contains the MSFS `DriverEntry`.

It registers major functions for create, create mailslot, close, read, write, query/set information, and filesystem control. Directory control, flush, shutdown, and security dispatchers are present only as commented placeholders.

`DriverEntry` creates `\Device\MailSlot` as a `FILE_DEVICE_MAILSLOT` device, enables `DO_DIRECT_IO`, initializes the device extension’s global FCB list and mutex, and returns success.

Research notes:
- The driver has no unload routine (`DriverUnload = NULL`).
- The device extension is only the global FCB list plus lock.
- MSFS is a kernel-mode driver module, not a user-mode service.
