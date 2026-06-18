# File Research: sources/os/bsd/dragonflybsd/sys/sys/efi.h

`efi.h` defines DragonFly's shared EFI data structures and constants. It covers EFI page sizing, selected EFI configuration table UUIDs, reset types, `efi_char`, `efi_status`, configuration table entries, memory descriptors, time/time-capability structures, table headers, runtime services, and the EFI system table.

Important ABI details include `EFIABI` using `__attribute__((ms_abi))` for runtime-service function pointers, EFI memory descriptor type and attribute constants, and `efi_next_descriptor()` for descriptor-table walking. Under `_KERNEL`, it exposes `efi_systbl_phys`.

This is a low-level firmware ABI header used by kernel EFI runtime/configuration consumers and EFI ioctls.
