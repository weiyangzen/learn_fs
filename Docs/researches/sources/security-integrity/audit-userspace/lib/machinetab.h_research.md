# sources/security-integrity/audit-userspace/lib/machinetab.h

Purpose: `_S(machine_id, name)` source table for audit machine aliases. It maps strings such as `i386`, `x86_64`, `ppc64le`, `s390x`, optional ARM/AArch64/RISC-V names, and optional `uring` to libaudit `MACH_*` ids.

Important APIs/types: it does not define functions by itself; it is included by generated lookup code and by `lookup_test.c` with `_S` redefined. The effective APIs are `audit_name_to_machine` and `audit_machine_to_name` in `lookup_table.c`.

Control flow: inclusion-time data expansion only. Ordering matters for reverse lookup because several names map to the same id, so canonical output is the first generated reverse-table match.

State and persistence: no runtime state. Feature macros decide which aliases compile into the binary.

Dependencies and integration: includes `config.h` and depends on `WITH_ARM`, `WITH_AARCH64`, `WITH_IO_URING`, and `WITH_RISCV`. It integrates with ELF architecture translation through `lookup_table.c`'s `elftab`.

Risks and test signals: alias changes can alter printed architecture names. `lookup_test.c` excludes several i386 and ARM aliases when testing reverse lookup because one numeric id has multiple accepted strings.
