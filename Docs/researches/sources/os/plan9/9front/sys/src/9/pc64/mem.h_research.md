# File Research: sources/os/plan9/9front/sys/src/9/pc64/mem.h

PC64 memory layout, page-table, segment, selector, and low-level machine constants shared by C and assembly.

Key contents:
- Binary size constants (`KiB` through `EiB`), alignment helpers, word/page sizes, page rounding, block/FPU alignment, and CPU/kernel stack sizes.
- Time constants for tick rate and conversion macros.
- User address layout: `UTZERO`, canonical user mask, `USTKTOP`, and user stack size.
- Kernel address layout: high-half `KZERO`, text start `KTZERO`, `VMAP`, `KMAP`, and their sizes.
- Fixed bootstrap physical/virtual addresses for boot args, AP bootstrap, IDT, reboot code, CPU0 PML4/PDP/PD pages, GDT, and `Mach`.
- Segment numbers, selectors, descriptor bit fields, and GDT sizing.
- Virtual and physical MMU constants: PTE map sizes, page-table levels/index macros, PTE flags, no-execute bit, PAT write-combining entry, and page color stub.
- Assembly register aliases for `m` and `up`.

Notable dependencies:
- Used directly by both C and assembly; constants must remain assembler-compatible.

Research notes:
- The file encodes the kernel’s high-half layout and the special early-boot pages assumed by `l.s`, `main.c`, `mmu.c`, and `apbootstrap.s`.
- `PTENOEXEC` depends on `m->havenx`, so it is not a pure constant expression in C use.
