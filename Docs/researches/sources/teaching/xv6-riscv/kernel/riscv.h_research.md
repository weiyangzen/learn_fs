# File Research: sources/teaching/xv6-riscv/kernel/riscv.h

Defines RISC-V CSR helpers, page-table types, status bits, interrupt helpers, and Sv39 paging macros.

Important contents:
- Inline CSR read/write helpers for machine and supervisor registers.
- Interrupt enable/disable helpers: `intr_on`, `intr_off`, `intr_get`.
- Hart/thread pointer helpers: `r_tp`, `w_tp`.
- `sfence_vma()` TLB flush.
- Types: `pte_t`, `pagetable_t`.
- Page constants and rounding macros.
- PTE bits, PA/PTE conversion, page-table index extraction, and `MAXVA`.

Filesystem relevance: supports VM and trap paths needed by syscalls, user copies, lazy page faults, and device interrupt handling. The page constants also define kernel allocation granularity.
