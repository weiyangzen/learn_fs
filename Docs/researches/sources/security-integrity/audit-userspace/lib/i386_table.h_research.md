# sources/security-integrity/audit-userspace/lib/i386_table.h

Purpose: Source table mapping i386 Linux syscall numbers to names for generated libaudit lookup code.

Important structure: `_S(number, "name")` entries include legacy i386 syscalls (`fork`, `oldstat`, `stty`, `gtty`, `mpx`) and modern additions up to `rseq_slice_yield`.

Control flow: No runtime control flow. `gen_i386_tables_h` generates `i386_tables.h` with duplicate-int support and lower-case name lookups.

State and persistence: Static syscall ABI mapping compiled into libaudit.

Dependencies and integration: Always part of `BUILT_SOURCES` in `lib/Makefile.am`. Used when parsing/displaying rules for `MACH_X86` or 32-bit `b32` rules on x86_64.

Risks: i386 has legacy and obsolete syscall names that must remain for ABI compatibility. Wrong numbers break audit rules on 32-bit x86 and compat syscalls.

Test signals: Round-trip lookups for legacy and modern syscalls, `arch=b32` parsing on x86_64, and generated table comparison with kernel syscall definitions.
