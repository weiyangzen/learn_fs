# File Research: sources/os/plan9/9front/sys/src/9/pc64/mmu.c

amd64 MMU, GDT/TSS setup, kernel mapping hardening, page-table allocation, process address-space switching, temporary mappings, VMAP mappings, PAT write combining, and early page preallocation.

Key behavior:
- Defines base GDT descriptors for kernel/user 64-bit code, user 32-bit code, and user data.
- `mmuinit` removes bootstrap double maps, marks kernel text read-only/non-text no-execute on CPU 0, allocates TSS, installs per-CPU GDT/TSS/IDT, sets GS base to `machp[machno]`, enables syscall MSRs, and points `Lstar` at `syscallentry`.
- `kaddr` and `paddr` validate physical/virtual address conversions.
- `mmualloc` manages per-CPU and global pools of `MMU` page-table descriptors and page-table pages.
- `mmucreate` and `mmuwalk` create or traverse hierarchical page tables for user, KMAP, and VMAP/KZERO addresses.
- `kernelro` splits large pages as needed, clears write permission on kernel text, and sets NX on non-text mappings except AP bootstrap.
- `pmap` and `punmap` create/remove kernel mappings, using 2MB pages when alignment and size permit.
- `mmuzap`, `mmuswitch`, `mmurelease`, and `flushmmu` manage per-process page-table roots and TLB context.
- `putmmu` installs user mappings; `checkmmu` diagnoses mismatches.
- `kmap` and `kunmap` create temporary per-process KMAP mappings for pages not directly reachable through KZERO.
- `vmap` maps physical device memory into the VMAP window as uncached, writable, no-execute; `vunmap` only validates the address.
- `patwc` changes mapped pages to the configured PAT write-combining entry.
- `preallocpages` reserves high memory for `palloc.pages` and the MMU page-table pool before normal page initialization.

Notable dependencies:
- Page constants and selectors from `mem.h`.
- Process `PMMU` fields from `dat.h`.
- Physical allocator and page-cache structures from the port layer.

Research notes:
- VMAP and KZERO PDPs are shared between processors; `vmap` comments explicitly note no synchronization is performed for that shared setup.
- `vunmap` is effectively a validation stub, not an unmapper.
- Kernel hardening relies on NX support through `m->havenx`; without NX, `PTENOEXEC` contributes no bit.
