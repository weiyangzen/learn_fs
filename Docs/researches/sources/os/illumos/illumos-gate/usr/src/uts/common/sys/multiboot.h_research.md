# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot.h

Multiboot v1 boot protocol layout header for illumos kernel boot.

Key responsibilities:
- Defines Multiboot header magic, flags, checksums for 32-bit and 64-bit kernels, and bootloader magic.
- Defines the Multiboot image header fields required within the first 8 KiB of the loaded image.
- Defines ELF section table, module, memory map, drive info, and drive mode structures.
- Defines `multiboot_info_t` with flag bits for memory, boot device, command line, modules, symbols, memory map, drive info, config table, boot loader name, APM, and VBE/video data.
- Adds illumos-specific `sol_netinfo` for diskless/network boot metadata.

Dependencies:
- Non-assembly users include `sys/types.h` and `sys/types32.h`.

Notable risks:
- All pointer fields are 32-bit physical/loader addresses; 64-bit kernel code must translate carefully.
- Memory map walking follows Multiboot’s variable-sized records, not a normal fixed array.
