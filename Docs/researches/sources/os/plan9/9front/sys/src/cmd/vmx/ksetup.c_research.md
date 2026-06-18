# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/ksetup.c

This file loads guest kernels and prepares boot protocol data for Multiboot, OpenBSD ELF, and Linux boot-protocol kernels.

Key behavior:
- Provides packing helpers for mixed 32/64-bit boot structures, BIOS memory-map export, command-line construction, and boot module loading.
- `trymultiboot` validates a Multiboot header, loads the kernel image, builds a multiboot info block with memory map, cmdline, modules, and framebuffer info, then seeds EAX/EBX/PC.
- ELF support parses 32/64-bit little-endian ELF headers, program headers, section headers, symbols, string tables, and loadable segments, rejecting dynamic/interpreter images.
- OpenBSD support detects `ostype` or ramdisk symbols, preserves selected debug/symbol sections, builds bootarg chains for memory map, console, DDB, EFI framebuffer, and parses OpenBSD-specific command-line settings.
- Linux support validates boot protocol >= 2.06, loads bzImage payload, builds zero page, cmdline, optional initrd, screen info, GDT, E820 map, and register state.
- `loadkernel` tries Multiboot, ELF/OpenBSD, then Linux.

Integration and risks:
- Strongly tied to guest memory availability through `gptr`, `gpa`, `gavail`, and `mmap`.
- OpenBSD/Linux boot structs are hand-packed at fixed offsets; protocol drift can break newer kernels.
