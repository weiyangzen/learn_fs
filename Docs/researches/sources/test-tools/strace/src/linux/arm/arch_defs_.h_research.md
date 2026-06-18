# sources/test-tools/strace/src/linux/arm/arch_defs_.h

Purpose: declares strace compile-time personality features for the `arm` Linux backend, including HAVE_ARCH_OLD_MMAP, HAVE_ARCH_OLD_SELECT, HAVE_ARCH_UID16_SYSCALLS, CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL, PERSONALITY0_AUDIT_ARCH, PERSONALITY0_AUDIT_ARCH.

Important APIs/types/functions: preprocessor macros control feature gates such as old mmap/select, UID16 syscalls, dedicated error registers, supported personalities, and audit arch tuples (AUDIT_ARCH_ARMEB, 0 ; AUDIT_ARCH_ARM, 0 ).

Control flow: no executable code. The main Linux backend includes this header while building architecture-specific syscall decoding and personality setup.

State/persistence behavior: static build-time configuration only; it influences how `struct tcb` register state is interpreted but stores no runtime state itself.

Dependencies/integration: depends on Linux audit architecture constants and may include generated base-number headers (no local includes).

Risks/test signals: incorrect feature macros select wrong syscall tables or legacy decoders; validate with architecture build tests, audit-personality checks, and traces of legacy mmap/select or UID16 syscalls when enabled.

Source-read signal: reviewed complete local file (16 lines).
