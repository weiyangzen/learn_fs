# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi.h

This header defines UEFI GUIDs, memory-map data types, EFI memory descriptors, and 32-bit/64-bit EFI system table layouts based on UEFI specification data.

Key contents:
- EFI configuration table GUID macros for global variables, MPS, ACPI, SMBIOS/SMBIOS3, SAL, FDT, DXE services, HOB list, memory type information, debug image info, and EFI properties.
- `efi_guid_t` as an aligned `struct uuid`.
- EFI physical and virtual address typedefs.
- `EFI_MEMORY_TYPE` enum including loader, boot services, runtime services, conventional, unusable, ACPI, MMIO, PAL, persistent, and unaccepted memory types.
- EFI memory attribute bits for caching, write/read/execute protection, nonvolatile/more-reliable/read-only memory, and runtime mapping.
- `EFI_MEMORY_DESCRIPTOR`.
- `EFI_TABLE_HEADER`.
- Revision helpers `EFI_REV`, `EFI_REV_MAJOR`, and `EFI_REV_MINOR`.
- EFI system table signature.
- 32-bit and 64-bit pointer typedefs plus packed configuration table and system table layouts:
  - `EFI_CONFIGURATION_TABLE32`
  - `EFI_CONFIGURATION_TABLE64`
  - `EFI_SYSTEM_TABLE32`
  - `EFI_SYSTEM_TABLE64`

Dependencies:
- Includes `sys/uuid.h`.
- Uses packed/aligned attributes.
- Uses C++ guards.

Research notes:
- This is firmware ABI layout, so packing and field widths are critical.
- `EFI_REV(x, y)` uses logical OR in the macro body rather than bitwise OR; readers should preserve existing behavior unless intentionally fixing ABI-facing code.
- Filesystem/storage relevance is boot and platform discovery: EFI memory and table parsing supports boot-time device/platform setup, while GPT handling is in `efi_partition.h`.
