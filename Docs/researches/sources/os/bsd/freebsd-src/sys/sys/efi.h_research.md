# File Research: sources/os/bsd/freebsd-src/sys/sys/efi.h

## Purpose
Defines FreeBSD EFI/UEFI data structures, GUIDs, memory descriptors, runtime service interfaces, and kernel EFI operation wrappers.

## Main Elements
- Page constants and known configuration table GUIDs for SMBIOS, ESRT, properties, memory attributes, and Linux memreserve.
- EFI reset enum, EFI character/status types, and `efi_guid_t`.
- Configuration table, memory descriptor, time, time capabilities, table header, ESRT, properties, and memory attribute table structures.
- Kernel runtime table `struct efi_rt` when EFI ABI attributes are available.
- Kernel system table `struct efi_systbl` and `efi_systbl_phys`.
- Linux EFI memreserve linked-table structures.
- MD EFI functions for entering/leaving EFI calls, physical-to-KVA, runtime arch calls, and 1:1 maps.
- `struct efi_ops` virtualizes EFI runtime/table/variable/time operations.
- Inline public wrappers return `ENXIO` when the active operation is unavailable.
- `efi_status_to_errno()` maps EFI statuses to errno.

## Dependencies And Integration
Includes `machine/efi.h` and `sys/efi-freebsd.h`; integrates with EFI runtime services, loader-provided metadata, platform firmware, and `/dev/efi`.

## Risk Notes
Runtime EFI calls are firmware-sensitive and may require special mappings/calling conventions. The operation table permits hypervisor-specific backends, so callers must handle `ENXIO`.
