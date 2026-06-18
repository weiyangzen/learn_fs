# File Research: sources/os/bsd/freebsd-src/sys/sys/efiio.h

## Purpose
Defines `/dev/efi` ioctl payloads for EFI table lookup, time, variable, and wake-time operations.

## Main Elements
- `efi_get_table_ioctl` carries userspace buffer pointer, EFI GUID, table length, and buffer length.
- `efi_var_ioctl` carries wide-char variable name, vendor GUID, attributes, data pointer, and byte size.
- `efi_waketime_ioctl` carries wake time and enabled/pending flags.
- Ioctls: get table, get/set time, variable get/next/set, get/set wake time.
- Compatibility `_WANT_EFI_IOC` structures preserve old `struct uuid` field names for pre-16 userland.
- Static assertions verify UUID and EFI GUID size/layout compatibility for ioctl structs.

## Dependencies And Integration
Includes `ioccom`, `uuid`, and `efi`. Used by EFI device driver and userland EFI variable/table tools.

## Risk Notes
The new ABI uses `efi_guid_t`; old compatibility structs are planned for removal in FreeBSD 16. Ioctl handlers must validate user pointers and byte-vs-wide-character sizes.
