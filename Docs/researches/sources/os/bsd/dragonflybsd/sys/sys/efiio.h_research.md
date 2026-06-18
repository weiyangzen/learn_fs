# File Research: sources/os/bsd/dragonflybsd/sys/sys/efiio.h

`efiio.h` defines the ioctl interface for EFI services exposed through a device interface. It includes `ioccom.h`, `uuid.h`, and `efi.h`.

The ABI structures are `efi_get_table_ioc`, for looking up EFI configuration tables by UUID, and `efi_var_ioc`, for getting, iterating, and setting EFI variables by wide-character name, vendor UUID, attributes, and data buffer.

It declares ioctl command numbers for table lookup, time get/set, variable get/next/set. This header is shared by userland tools and the kernel EFI device implementation.
