# File Research: sources/teaching/os161/kern/include/vm.h

Declares VM subsystem entry points and common fault constants. It includes `machine/vm.h`, defines `VM_FAULT_READ`, `VM_FAULT_WRITE`, and `VM_FAULT_READONLY`, and exports `vm_bootstrap`, `vm_fault`, `alloc_kpages`, `free_kpages`, `coremap_used_bytes`, and `vm_tlbshootdown`.

This is intentionally sparse and assignment-oriented. It forms the contract among trap handling, kmalloc page allocation, coremap accounting, and interprocessor TLB shootdown handling.

Risk areas are implementation-dependent: address validation, fault-type handling, physical page ownership, and shootdown correctness are not resolved in this header.
