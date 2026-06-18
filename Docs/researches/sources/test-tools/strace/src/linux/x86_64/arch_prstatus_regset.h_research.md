<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h

Purpose: declares the x86_64 general-purpose register-set structure used for PRSTATUS decoding.
Important APIs/types/functions: `struct_prstatus_regset` with `r15..gs` fields in kernel order and `HAVE_ARCH_PRSTATUS_REGSET`.
Control flow: preprocessor selects i386 layout for `MPERS_IS_m32`, otherwise guards the native structure. State and persistence behavior: no mutable state.
Dependencies and integration points: consumed by `arch_prstatus_regset.c` and generic regset code. Risks: any layout mismatch affects syscall number, PC/SP, and register output. Test signals: compile and trace tests comparing printed register sets with ptrace data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_prstatus_regset.h -->
