# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pci.c

`pci.c` caches opened PCI config-space raw files for the emulator. `pciopen` maps a BDF to `#$/pci/<bus>.<dev>.<fn>raw`, opens it `ORDWR`, and stores the result in a linked list even if open failed.

`pcicfgr` and `pcicfgw` perform `pread`/`pwrite` at config offsets. This backs real-mode I/O ports `0xcf8`/`0xcfc` in `main.c`.
