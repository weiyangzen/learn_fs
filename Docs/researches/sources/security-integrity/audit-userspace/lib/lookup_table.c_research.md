# sources/security-integrity/audit-userspace/lib/lookup_table.c

Purpose: central libaudit lookup bridge between human rule/log names and numeric kernel audit constants. It includes generated table headers and exposes conversion APIs for fields, syscalls, io_uring operations, flags, actions, message types, machine names, ELF audit architecture values, errno names, file types, filesystem types, and permission classes.

Important APIs: `audit_name_to_syscall`, `audit_syscall_to_name`, `audit_name_to_uringop`, `audit_uringop_to_name`, `audit_name_to_msg_type`, `audit_msg_type_to_name`, `audit_name_to_machine`, `audit_machine_to_elf`, `audit_elf_to_machine`, `audit_name_to_errno`, `audit_errno_to_name`, and the field/flag/action/ftype/fstype/perm lookup wrappers. Most call generated `*_s2i` and `*_i2s` functions from `gen_tables.h` output.

Control flow: syscall lookup switches on libaudit machine ids and dispatches to the architecture-specific table; `MACH_IO_URING` dispatches to the io_uring table. Message type lookup first tries the table, then accepts `UNKNOWN[n]` and leading decimal strings as fallbacks. ELF conversion linearly scans `elftab`.

State and persistence: no persistent state. The only state is the static `elftab` table compiled under architecture feature macros. The file changes process-global `errno` before numeric fallbacks and relies on `_audit_elf` elsewhere through consumers, not here.

Dependencies and integration: depends on `libaudit.h`, generated `*_tables.h`, `msg_typetabs.h`, `machinetabs.h`, `optabs.h`, and optional `WITH_ARM`, `WITH_AARCH64`, `WITH_RISCV`, `WITH_IO_URING`, `NO_TABLES`. It is used by rule parsers, auditctl listing, ausearch/aureport interpretation, and tests.

Risks and test signals: correctness depends on generated tables matching kernel UAPI and architecture syscall numbering. `audit_name_to_msg_type` uses bounded local copy but intentionally truncates long `UNKNOWN[]` numbers. `lookup_test.c` is the direct regression signal for bidirectional table coverage and alias exceptions.
