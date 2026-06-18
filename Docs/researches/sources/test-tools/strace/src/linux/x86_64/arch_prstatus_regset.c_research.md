<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c

Purpose: decodes x86_64 `NT_PRSTATUS` general register-set data.
Important APIs/types/functions: `arch_decode_prstatus_regset`, `struct_prstatus_regset`, partial-size checks, `PRINT_FIELD_X`, and i386 mpers include.
Control flow: rejects zero/non-8-byte-aligned sizes, fetches the bounded payload, prints registers in kernel layout order only when the supplied size reaches each field, and marks trailing unknown data.
State and persistence behavior: stateless tracee-memory read. Dependencies and integration points: used by ptrace regset display and `arch_prstatus_regset.h`.
Risks: field order must match kernel ABI exactly; partial-size logic can hide valid trailing fields if offsets change. Test signals: native x86_64 regset fixtures plus oversized and truncated payload tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.c -->
