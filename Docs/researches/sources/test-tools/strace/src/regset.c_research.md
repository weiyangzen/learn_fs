# sources/test-tools/strace/src/regset.c

Purpose: Provides generic wrappers for decoding ELF note regsets, delegating to architecture register printers.

Important APIs/types/functions: functions for `decode_prstatus_regset` and `decode_fpregset`-style entry points.

Control flow: accepts tracee address and length, validates/fetches expected register-set layouts where possible, and prints raw address or unavailable output when decoding is not supported.

State and persistence: stateless.

Dependencies/integration: `regs.h`, architecture-specific register definitions, ptrace regset decoder in `ptrace.c`, and iovec length handling.

Risks: regset layouts are architecture-specific and variable-length; overly strict size checks can hide valid partial data, while loose checks can misdecode.

Test signals: `PTRACE_GETREGSET` for `NT_PRSTATUS` and `NT_FPREGSET`, invalid iovec base, changed iovec length, and unsupported note types.
