# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc.c

Implements SPARC/SPARC64-compatible machine-dependent crash dump translation. It uses MMU metadata written into the CPU segment by `pmap_dumpmmu()`.

Key behavior:
- `_kvm_initvtop()` reads CPU type, sets page size/shift for sun4/sun4c/sun4m/sun4u, and computes PTEs per segment group.
- `_kvm_kvatop()` dispatches to sun4/sun4c, sun4m, or sun4u translation.
- sun4/sun4c uses segment maps and PMEG PTE arrays.
- sun4m uses segment maps and reads SRMMU PTEs from the dump.
- sun4u handles a 4MB locked TLB region and then consults sparc64-style segment/page table data.
- `_kvm_pa2off()` maps sparse physical addresses into packed dump offsets using CPU segment memory ranges.
- `_kvm_mdopen()` uses `__ps_strings + 1` for max user VA.

Notable concern: some pointer arithmetic casts `kd->cpu_data` through `int`, reflecting older 32-bit assumptions in code that also handles sparc64-flavored data.
