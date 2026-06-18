# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2_impl.h

dboot helper interface for consuming Multiboot 2 information.

Key responsibilities:
- Declares helpers to find tags, get command line, count modules, retrieve module start/end/cmdline values, and get memory map tags.
- Declares basic memory info retrieval.
- Declares indexed accessors for Multiboot memory map and EFI memory map entry length, base, and type.
- Declares helpers to count memory map entries and compute the highest referenced address.

Dependencies:
- Includes `sys/multiboot2.h`; uses `boolean_t`, `uint32_t`, `uint64_t`, and `paddr_t` from surrounding boot/kernel types.

Notable risks:
- Accessors must handle packed, variable-sized tags and bounds correctly during early boot.
- These functions operate before normal kernel services are fully available.
