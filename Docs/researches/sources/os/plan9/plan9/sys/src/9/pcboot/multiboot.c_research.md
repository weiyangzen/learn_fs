# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/multiboot.c

This file constructs a Multiboot information block for transferring control from the 32-bit bootstrap to a 64-bit kernel.

Key responsibilities:
- Maintains global `mbhdr`, `multibootheader`, `mmap`, and `nmmap`.
- `mkmultiboot` reuses low BIOS table memory at `BIOSTABLES` for the Multiboot header and memory map.
- Copies the collected memory map into low memory, sets the command-line pointer to `BOOTLINE`, and sets `Fcmdline` and `Fmmap` flags as appropriate.
- Converts the final header pointer to a physical address before handoff.

Filesystem/storage relevance:
- This is not a filesystem component, but it preserves boot command-line and memory-map state needed by the next kernel, including storage boot parameters.
