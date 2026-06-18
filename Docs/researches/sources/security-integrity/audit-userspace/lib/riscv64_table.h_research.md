# sources/security-integrity/audit-userspace/lib/riscv64_table.h

Purpose: RISC-V 64-bit syscall table for libaudit. It maps RISC-V syscall numbers to names, including generic syscalls, RISC-V-specific `riscv_hwprobe` and `riscv_flush_icache`, and modern additions such as `openat2`, `fchmodat2`, `mseal`, `listns`, and `rseq_slice_yield`.

Important APIs/types: feeds generated `riscv64_syscall_s2i` and `riscv64_syscall_i2s` for `MACH_RISCV64`.

Control flow: static include-time expansion, with intentional ABI gaps.

State and persistence: none.

Dependencies and integration: compiled under `WITH_RISCV`, used by `lookup_table.c`, and included by `lookup_test.c`.

Risks and test signals: must stay synchronized with Linux RISC-V syscall numbers; mismatches affect both rule creation and rule listing. Lookup tests validate present entries but not semantic auditability.
