# sources/test-tools/strace/src/regs.h

Purpose: Declares architecture register-set decoding entry points used by ptrace and related code.

Important APIs/types/functions: prototypes such as `decode_pt_regs`, `decode_pt_fpregs`, and regset decoders for `NT_PRSTATUS`/`NT_FPREGSET`.

Control flow: header-only; architecture-specific `.c` files provide concrete decoders.

State and persistence: none.

Dependencies/integration: included by `ptrace.c` and regset code; depends on `struct tcb` and address/length types.

Risks: architecture conditional availability must match build configuration. Prototype drift breaks ptrace register decoding.

Test signals: ptrace get/set regs and get/set regset tests on supported architectures plus compile-only coverage elsewhere.
