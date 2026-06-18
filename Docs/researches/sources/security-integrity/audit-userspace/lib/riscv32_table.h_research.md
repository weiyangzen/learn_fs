# sources/security-integrity/audit-userspace/lib/riscv32_table.h

Purpose: RISC-V 32-bit syscall table for libaudit. It reflects the generic syscall base with 32-bit variants such as `fcntl64`, `statfs64`, `truncate64`, time64 syscalls, and current newer syscalls through namespace/list operations.

Important APIs/types: compiled into generated `riscv32_syscall_s2i` and `riscv32_syscall_i2s`, used when `audit_name_to_syscall` receives `MACH_RISCV32`.

Control flow: static `_S` expansions only. Gaps are preserved where the ABI has no auditable entry or a skipped number.

State and persistence: none.

Dependencies and integration: compiled under `WITH_RISCV` and included by `lookup_test.c` when that feature is enabled.

Risks and test signals: the table is new and must track RISC-V UAPI syscall additions closely. Incorrect 32-bit vs 64-bit naming can make `auditctl` load rules that match the wrong syscall number. Lookup tests verify round-trip entries under `WITH_RISCV`.
