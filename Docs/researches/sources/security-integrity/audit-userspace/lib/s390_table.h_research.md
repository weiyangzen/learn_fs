# sources/security-integrity/audit-userspace/lib/s390_table.h

Purpose: 32-bit s390 syscall table for audit rule parsing and listing. It includes legacy s390 calls, 32-bit uid/gid variants, time64 additions, s390-specific PCI/runtime calls, and modern common syscalls.

Important APIs/types: generates `s390_syscall_s2i` and `s390_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_S390`.

Control flow: static `_S(number, name)` data expansion with reserved/commented gaps.

State and persistence: none.

Dependencies and integration: compiled into libaudit and included by `lookup_test.c`.

Risks and test signals: s390 has many compatibility and legacy names; stale entries can break 32-bit compatibility auditing. `lookup_test.c` checks bidirectional mapping for all included entries.
