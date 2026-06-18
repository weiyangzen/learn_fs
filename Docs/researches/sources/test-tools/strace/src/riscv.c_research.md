# sources/test-tools/strace/src/riscv.c

Purpose: RISC-V architecture-specific syscall/register support.

Important APIs/types/functions: architecture hooks for syscall number, argument, or return-value extraction and register printing as required by the strace core.

Control flow: reads RISC-V tracee register state through architecture-specific ptrace APIs and maps registers into strace's generic `tcp->u_arg`/syscall number fields.

State and persistence: updates per-tracee syscall context, not durable global state.

Dependencies/integration: core arch hooks, ptrace register definitions, and syscall dispatch.

Risks: ABI differences for 32/64-bit RISC-V and syscall restart/error conventions can cause wrong arguments or return values.

Test signals: RISC-V architecture CI or cross tests for syscall argument decoding, restart handling, and ptrace register fetch failures.
