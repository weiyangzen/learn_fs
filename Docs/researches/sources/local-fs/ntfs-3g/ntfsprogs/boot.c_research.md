# File Research: sources/local-fs/ntfs-3g/ntfsprogs/boot.c

Defines `boot_array`, a 4136-byte static boot-code template used by `mkntfs` when creating an NTFS boot sector/boot area. The template begins with the NTFS jump instruction and OEM ID, leaves space for BIOS/device parameter fields, and contains simple x86 boot code that prints a non-bootable-disk message, waits for a key, and invokes BIOS bootstrap retry.

The array pads the boot sector to the signature location and ends with the standard `0x55 0xaa` boot signature. The comments identify offsets for the boot code and message, with the BPB/device-parameter region intentionally zeroed for later formatting code to fill.

There is no runtime logic; correctness depends on `mkntfs` copying and patching the byte template consistently with NTFS boot-sector layout.
