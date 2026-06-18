# sources/security-integrity/audit-userspace/lib/x86_64_table.h

Purpose: x86_64 syscall number table for libaudit. It maps canonical syscall names from `read` through modern entries such as `openat2`, `fchmodat2`, `mseal`, `listns`, and `rseq_slice_yield`.

Important APIs/types: generates `x86_64_syscall_s2i` and `x86_64_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_86_64`.

Control flow: static `_S` expansion. It intentionally comments nontraditional `uretprobe` and `uprobe` and reserves a range before common additions.

State and persistence: none.

Dependencies and integration: used by auditctl rule parsing/listing, ausearch interpretation, and `lookup_test.c`.

Risks and test signals: x86_64 is a common deployment target, so stale entries have high user impact. `auditctl.c::check_rule_mismatch` warns when names map differently across native and compat arch without explicit `arch=`.
