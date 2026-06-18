# sources/security-integrity/audit-userspace/lib/ppc_table.h

Purpose: PowerPC syscall number-to-name table for libaudit syscall parsing and printing. It spans legacy calls, modern network/socket calls, io_uring setup calls, landlock, xattr-at, namespace, and recent syscalls through `rseq_slice_yield`.

Important APIs/types: no standalone functions; included by generated `ppc_syscall_s2i` and `ppc_syscall_i2s` used by `audit_name_to_syscall` for `MACH_PPC`, `MACH_PPC64`, and `MACH_PPC64LE`.

Control flow: static `_S(number, name)` expansion. Numeric gaps and reserved comments are intentional ABI records.

State and persistence: no state.

Dependencies and integration: compiled into libaudit unless `NO_TABLES`; included directly by `lookup_test.c`.

Risks and test signals: wrong numbers break audit rule matching on PPC families. Because 32/64 PPC share this table in lookup dispatch, architecture-specific divergences must be handled carefully. `lookup_test.c` checks bidirectional lookups for all entries.
