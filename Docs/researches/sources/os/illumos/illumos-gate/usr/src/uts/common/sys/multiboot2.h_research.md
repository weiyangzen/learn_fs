# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2.h

Multiboot 2 protocol constants and packed structure definitions.

Key responsibilities:
- Defines Multiboot 2 search/alignment constants, header and bootloader magic, module/info alignment, tag IDs, header tag IDs, architecture IDs, optional tag flag, load preferences, and console flags.
- Defines packed header and header-tag structures for information requests, load addresses, entry address, console flags, framebuffer, module alignment, and relocatable kernels.
- Defines memory map entries and memory type constants.
- Defines generic tag and info-header structures plus typed tags for command line, bootloader name, modules, basic memory, boot device, memory map, VBE, framebuffer, ELF sections, APM, EFI32/EFI64, SMBIOS, ACPI, network, EFI memory map, EFI image handles, and load base address.
- Represents variable-length data with flexible arrays in string, module command line, memory maps, ELF sections, SMBIOS, ACPI, and network tags.

Dependencies:
- Non-assembly users include `sys/stdint.h`; structures are explicitly `#pragma pack(1)`.

Notable risks:
- Packed wire/bootloader ABI; natural alignment assumptions are unsafe.
- Header comments warn the spec documentation was inaccurate when written and GRUB 2 behavior is the practical reference.
