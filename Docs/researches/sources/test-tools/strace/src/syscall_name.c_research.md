# sources/test-tools/strace/src/syscall_name.c

Purpose: maps a syscall number plus Linux audit architecture to a syscall name and optional number prefix.

Important APIs/types/functions: `audit_arch_vec`, `syscall_name_arch`, `nr_prefix`, `shuffle_scno_pers`, `scno_pers_is_valid`, `sysent_vec`, and personality audit-arch constants.

Control flow: converts the input to `kernel_ulong_t` only if lossless, scans supported personalities for a matching audit architecture, shuffles the syscall number into that personality's table space, validates it, optionally supplies a prefix for the current personality, and returns the table name.

State and persistence behavior: reads global `current_personality`; no mutation.

Dependencies and integration points: used by filters and user-facing decoding that need architecture-qualified syscall names; depends on generated xlat macro constants and syscall tables.

Risks: audit architecture mismatches and invalid shuffled numbers return NULL; prefix handling differs for current vs non-current personality.

Test signals: native/compat/x32 audit arch lookups, invalid numbers, too-large `ull_nr`, prefix output for current personality, and NULL prefix for non-current matches.
