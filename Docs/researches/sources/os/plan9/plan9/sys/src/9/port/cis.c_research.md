# File Research: sources/os/plan9/plan9/sys/src/9/port/cis.c

This file parses PCMCIA Card Information Structure tuples.

Key responsibilities:
- Reads CIS bytes from attribute or memory space through `pcmmap`.
- `pcmcistuple` fetches a requested tuple/subtuple.
- `pcmcisread` parses all relevant tuples into a `PCMslot`.
- Handles version strings, configuration register metadata, configuration table entries, voltage/current descriptors, timing descriptors, I/O ranges, IRQ masks, and memory windows.
- Supports multifunction CIS long-link traversal.

Filesystem/storage relevance:
- Supports PCMCIA device configuration, including storage/network cards that may later expose filesystems or block devices.
- Not itself a filesystem component.
