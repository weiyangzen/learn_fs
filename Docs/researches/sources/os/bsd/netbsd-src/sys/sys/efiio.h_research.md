# File Research: sources/os/bsd/netbsd-src/sys/sys/efiio.h

Defines EFI runtime table and variable ioctl ABI.

Key content:
- EFI variable attribute flags: non-volatile, boot service, runtime, hardware error record, authenticated write, time-based authenticated write, append write, enhanced authenticated access.
- `struct efi_get_table_ioc`: buffer, UUID, table length, buffer length.
- `struct efi_var_ioc`: UTF-16 variable name buffer, name size, vendor UUID, attributes, data buffer, data size.
- Ioctls: `EFIIOC_GET_TABLE`, `EFIIOC_VAR_GET`, `EFIIOC_VAR_NEXT`, `EFIIOC_VAR_SET`.

Important behavior:
- Includes `sys/uuid.h`.
- Provides typed ABI for EFI table retrieval and variable enumeration/get/set.
