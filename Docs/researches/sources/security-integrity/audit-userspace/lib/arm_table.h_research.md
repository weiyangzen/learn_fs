# sources/security-integrity/audit-userspace/lib/arm_table.h

Purpose: Source table mapping 32-bit ARM EABI syscall numbers to names for generated libaudit lookup code.

Important structure: `_S(number, "name")` entries beginning with legacy syscalls (`restart_syscall`, `exit`, `fork`, `read`, `open`) and extending through modern syscalls (`clone3`, `openat2`, `landlock_*`, `futex_*`, `mseal`, `setxattrat`, `file_getattr`, `listns`, `rseq_slice_yield`). Some numbers are absent where the ARM ABI has gaps or unavailable calls.

Control flow: No runtime control flow; `gen_arm_tables_h` generates `arm_tables.h` when `USE_ARM` is enabled.

State and persistence: Static ABI mapping used by libaudit rule parsing and display.

Dependencies and integration: Enabled by `--with-arm`. Integrated with `audit_determine_machine`, `audit_machine_to_elf`, and syscall name translation for `MACH_ARM`.

Risks: ARM syscall availability differs from AArch64 and x86; stale entries can create invalid rules or poor diagnostics. Gaps must be preserved accurately rather than compressed.

Test signals: Generated table compile, name/number round trips for representative old and new syscalls, and comparison with kernel ARM syscall headers.
