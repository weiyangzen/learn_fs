# File Research: sources/os/plan9/plan9/sys/src/9/pc/mmu.c

x86 MMU, segmentation, page-directory, device mapping, and temporary page mapping support for the Plan 9 PC kernel.

Key elements:
- Defines flat GDT descriptors for kernel/user code/data, 16-bit kernel code, and TSS.
- `mmuinit0` and `mmuinit` initialize GDT/IDT/TSS, install the recursive VPT mapping, mark kernel text read-only, and switch TSS/CR3.
- `memglobal` marks kernel mappings `PTEGLOBAL` when PGE is supported.
- `mmupdballoc`, `mmupdbfree`, `mmuptefree`, `mmuswitch`, `mmurelease`, `putmmu` implement per-process page directories and page-table page lifecycle.
- `mmuwalk` is the kernel page-table walker; before full MMU init it allocates tables with `rampage`.
- `vmap`, `vunmap`, `pdbmap`, `pdbunmap`, `vmapsync` manage global device mappings in the VMAP range.
- `kmap`, `kunmap` map physical `Page` objects into per-process temporary KMAP slots.
- `tmpmap`, `tmpunmap` provide a one-page temporary mapping for editing page directories.
- `kaddr`, `paddr`, `cankaddr` enforce/describe the KZERO direct map boundary.
- `countpagerefs`, `checkmmu` are debugging/accounting helpers.

Interactions:
- Depends on memory layout constants from `mem.h` and page allocation from port code.
- Supplies device memory mappings used by PCI, VGA, APIC, ACPI, and SCSI controller code.
- `memory.c` uses `pdbmap` and `mmuwalk` during bootstrap scanning.

Research notes:
- The VPT self-map is the central implementation detail: current page tables are edited via virtual addresses.
- VMAP mappings are mastered in `mach0->pdb` and lazily copied into process page directories on faults.
