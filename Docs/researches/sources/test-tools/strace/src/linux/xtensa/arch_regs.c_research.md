<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_regs.c -->
# sources/test-tools/strace/src/linux/xtensa/arch_regs.c

Purpose: defines Xtensa register storage and PC/SP macros.
Important APIs/types/functions: static `struct user_pt_regs xtensa_regs`, `ARCH_REGS_FOR_GETREGS`, `ARCH_PC_REG`, and windowed-stack `ARCH_SP_REG` expression.
Control flow: no functions; SP resolves through `windowbase * 4 + 1`. State and persistence behavior: static register snapshot updated by ptrace.
Dependencies and integration points: argument extraction, return handling, and stack traces. Risks: Xtensa register windows make incorrect windowbase handling especially visible. Test signals: Xtensa syscall and stack-pointer decode tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_regs.c -->
