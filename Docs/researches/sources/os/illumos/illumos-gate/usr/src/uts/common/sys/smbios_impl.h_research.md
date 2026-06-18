# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios_impl.h

## Role

Private implementation header for illumos SMBIOS parsing in libsmbios and the kernel SMBIOS provider. Public clients are explicitly directed to use `<smbios.h>` or `<sys/smbios.h>` instead.

## Key Contents

Defines packed SMBIOS wire-format structures for many DMTF structure types: BIOS, system, baseboard, chassis, processor, cache, port, slot, onboard devices, string tables, event log, memory arrays/devices/maps, pointer devices, battery, hardware security, probes, cooling devices, boot info, management/IPMI/power supply, additional information, TPM, processor-specific info, firmware inventory, string properties, and Sun OEM extensions.

Includes decode macros for BIOS extended ROM fields, chassis element types, cache size/configuration, hardware security bitfields, probe type/status, IPMI fields, and PSU characteristics.

Defines the internal `smb_struct_t` descriptor and `struct smbios_hdl`, including entry-point type, table buffer, parsed structure array, hash buckets, error state, ABI/library version, SMBIOS version, and flags.

## Interfaces

Declares internal lookup, string, version, error, allocation, free, and debug helpers such as `smb_lookup_type`, `smb_lookup_id`, `smb_strptr`, `smb_gteq`, `smb_set_errno`, `smb_open_error`, `smb_alloc`, and `smb_dprintf`.

## Design Notes

The file centralizes raw SMBIOS layout knowledge, including variable-length records and versioned structure continuations. It also defines base public-structure snapshots used to preserve ABI compatibility when public SMBIOS structures grow.
