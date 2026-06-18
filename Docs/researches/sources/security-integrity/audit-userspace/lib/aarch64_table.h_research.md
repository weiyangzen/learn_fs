# sources/security-integrity/audit-userspace/lib/aarch64_table.h

Purpose: Source table mapping AArch64 Linux syscall numbers to names for generated libaudit lookup code.

Important structure: A sequence of `_S(number, "name")` entries from low-number syscalls such as `io_setup`, `setxattr`, and `openat` through newer syscalls such as `landlock_*`, `mseal`, `setxattrat`, `open_tree_attr`, `file_getattr`, `listns`, and `rseq_slice_yield`.

Control flow: No runtime control flow. `lib/Makefile.am` builds `gen_aarch64_tables_h` with `TABLE_H="aarch64_table.h"` and emits `aarch64_tables.h` with lower-case string-to-int and int-to-string helpers.

State and persistence: Static source data that persists into generated headers and ultimately libaudit syscall translation APIs.

Dependencies and integration: Enabled only when configured with AArch64 support. Used by `audit_name_to_syscall`, `audit_syscall_to_name`, rule parsing for `arch=aarch64`, and permission-to-syscall expansion.

Risks: Syscall numbering must match the kernel ABI. Missing or wrong entries break audit rule parsing and user display for AArch64. Architecture-specific syscall absence matters because generic permission syscall lists may include names unavailable on this architecture.

Test signals: Generated table builds, `audit_name_to_syscall("openat2", MACH_AARCH64)`, reverse lookup checks, and comparison with current kernel syscall tables.
