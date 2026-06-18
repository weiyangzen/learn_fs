<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_defs_.h -->
# sources/test-tools/strace/src/linux/xtensa/arch_defs_.h

Purpose: declares Xtensa audit architecture metadata.
Important APIs/types/functions: `PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_XTENSA, 0 }`.
Control flow: compile-time metadata only. State and persistence behavior: no mutable state.
Dependencies and integration points: personality/audit matching in the generic Linux backend. Risks: wrong audit arch prevents correct syscall-info classification. Test signals: Xtensa build/config tests and audit-arch matching tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/arch_defs_.h -->
