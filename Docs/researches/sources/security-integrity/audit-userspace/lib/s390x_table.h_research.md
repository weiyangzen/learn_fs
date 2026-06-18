# sources/security-integrity/audit-userspace/lib/s390x_table.h

Purpose: 64-bit s390x syscall table for audit rule parsing and listing. It maps s390x syscall numbers to canonical names and preserves s390-specific calls and ABI gaps.

Important APIs/types: generates `s390x_syscall_s2i` and `s390x_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_S390X`.

Control flow: static table expansion. Some legacy or nontraditional entries are omitted/commented to avoid reporting them as ordinary syscalls.

State and persistence: none.

Dependencies and integration: used by libaudit lookup dispatch and direct lookup tests.

Risks and test signals: divergence between s390 and s390x numbering makes copy/paste changes risky. `auditctl.c::check_rule_mismatch` specifically compares 64-bit and 32-bit masks for several architectures, including s390x to s390, to warn about unspecified arch rules.
