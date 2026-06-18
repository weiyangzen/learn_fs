# File Research: sources/os/plan9/9front/sys/src/9/pc/pcipc.c

Implements PC PCI configuration-space access setup, PCI routing-table handling, southbridge IRQ link programming, PCI resource reservation/allocation, and PCI bus discovery.

Key behavior:
- Raw config accessors support PCI configuration mechanism #1 via ports `0xCF8/0xCFC` and mechanism #2 via `0xCF8/0xCFA`.
- `pcicfginit()` selects config mode unless BIOS mode is forced, scans PCI buses up to `pcimaxbno`, resets CardBus bridges encountered on bus 0, optionally allocates all bus windows when `*nobios` is set, reserves existing BAR resources, and applies PCI IRQ routing.
- `$PIR` parsing in `pcirouting()` validates checksum, finds the interrupt router southbridge, chooses matching chipset handlers, and updates device `PciINTL` values.
- Southbridge handler tables cover Intel PIIX/ICH/PCH families, VIA, OPTi, ALi, SiS, Cyrix, AMD, NVIDIA, ATI/AMD, ServerWorks, and others.
- `pcireserve()` reserves already assigned I/O/memory BARs and allocates address space for unassigned BARs using parent bridge windows when possible.
- `pcicfginit()` honors `*nobios`, `*pcibios`, `*nopcirouting`, `*pcimaxbno`, `*pcimaxdno`, and `*pcihinv`.

Research notes:
- This file is foundational for all PCI storage/display drivers in this group: AHCI, MMC, SCSI, VGA, and BIOS fallback all depend on correct PCI enumeration and BAR assignment.
- Some bridge entries intentionally have `nil` get/set handlers, meaning the router is recognized but not reprogrammed by this code.
- Resource reservation distinguishes I/O BARs from memory BARs and uses `ioreserve`, `ioreservewin`, `upaalloc`, and `upaallocwin`.
