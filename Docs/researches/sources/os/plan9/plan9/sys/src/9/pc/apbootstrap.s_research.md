# File Research: sources/os/plan9/plan9/sys/src/9/pc/apbootstrap.s

x86 application-processor bootstrap code for SMP startup.

Key responsibilities:
- Real-mode entry at `apbootstrap` far-jumps into `_apbootstrap`.
- Defines writable bootstrap data slots for AP entry vector, page directory base, and APIC value.
- Loads a minimal GDT, enables protected mode, installs segment registers, and far-jumps to 32-bit code.
- `_ap32` double-maps `KZERO` at virtual 0, loads CR3, enables paging/write-protect, and jumps into kernel virtual space.
- `_appg` removes the temporary zero mapping, flushes CR3, sets stack to `MACHADDR+MACHSIZE-4`, clears flags, pushes APIC argument, and calls the AP startup vector.
- Provides minimal GDT entries and pointer.

Important behavior:
- Must reside in low conventional memory on a 4 KiB boundary and effectively within the first 64 KiB due to shortcut addressing.
- The paging enable code must run from identity-mapped pages, hence the temporary double map.

Dependencies:
- Depends on x86 memory constants and descriptor macros from `mem.h`.
- Called by APIC/MP startup code after writing bootstrap data slots.

Notable risks:
- Very address-layout-sensitive; comments explicitly call out placement restrictions.
- Assumes page directory contains a valid kernel mapping at `KZERO`.
