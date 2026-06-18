<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/or1k_atomic.c -->
# sources/test-tools/strace/src/or1k_atomic.c

Purpose: architecture-specific decoder for OpenRISC `or1k_atomic` syscall.

Important APIs/types/functions: `SYS_FUNC(or1k_atomic)`, `OR1K_ATOMIC_*` operation constants, and `atomic_ops` xlat.

Control flow: under `OR1K`, prints operation type and then prints one, two, or three value arguments depending on the atomic operation; returns decoded with hex return formatting.

State and persistence behavior: no state.

Dependencies and integration points: compiled only for OR1K builds; integrated through the architecture syscall table.

Risks: operation constants are local definitions and must match the kernel ABI. Unsupported operations print only the type.

Test signals: OR1K syscall tests for swap, cmpxchg, decpos, arithmetic/bitwise ops, unknown type, and hex return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/or1k_atomic.c -->
