# File Research: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.h

ACPI table layout definitions used by minimal MP ACPI scanning and other PC firmware consumers.

Key elements:
- Defines common 36-byte SDT header embeddings for `Dsdt`, `Facp`, `Hpet`, `Madt`, and `Mcfg`.
- `Madt` includes LAPIC base address, flags, and variable MADT structures.
- `Mcfg` and `Mcfgd` describe PCI memory-mapped configuration regions.
- `Rsd` describes ACPI RSDP revision, RSDT address, XSDT address, and checksums.

Interactions:
- Included by `mpacpi.c`.
- Complements `sigsearch` from `memory.c` and `vmap` from `mmu.c`.

Research notes:
- Pure structure header; no behavior.
- Only MADT is used by the file group here.
