# File Research: sources/teaching/xv6-public/entry.S

Kernel entry assembly for the bootstrap processor.

Key behavior:
- Emits a multiboot header for GRUB-compatible booting.
- Defines `_start` as the physical address of `entry`.
- Enables 4 MiB page support with `CR4_PSE`.
- Loads `entrypgdir`, turns on paging and write-protect, sets the initial stack, and jumps to high-address `main`.
- Reserves the bootstrap stack with `.comm stack, KSTACKSIZE`.

Important interactions:
- Uses `entrypgdir` from `main.c`.
- Bridges from the bootloader’s physical jump to the kernel’s higher-half virtual mapping.
