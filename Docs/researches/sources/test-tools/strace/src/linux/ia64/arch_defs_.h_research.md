# sources/test-tools/strace/src/linux/ia64/arch_defs_.h

Purpose: declares strace compile-time personality features for the `ia64` Linux backend, including HAVE_ARCH_GETRVAL2, HAVE_ARCH_UID16_SYSCALLS, HAVE_ARCH_SA_RESTORER, HAVE_ARCH_DEDICATED_ERR_REG, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_IA64, SYSCALLENT_BASE_NR ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (syscallent_base_nr.h).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (14 lines).
