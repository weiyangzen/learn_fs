<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.c -->
# sources/test-tools/strace/tests/ipc.c

Purpose: Tests decoding of the legacy multiplexed `ipc` syscall and verifies that strace can split selected calls into SysV IPC names such as `semctl` and `msgrcv`.

Important APIs/types/functions: Uses `syscall(__NR_ipc)`, `<linux/ipc.h>`, fallback `SEMCTL` and `MSGRCV` constants, `ipc_call`, `ipc_call0`, `tail_alloc`, and `sprintrc`.

Control flow: Builds an encoded first argument from high garbage bits, IPC version, and call number. It first checks whether a `SEMCTL` call with a faulting pointer is decoded as `semctl`, iterates several raw call numbers with version 0 and 42, then conditionally tests versioned `SEMCTL` and `MSGRCV` output depending on kernel behavior.

State/persistence behavior: Uses faulting pointers and invalid arguments, so no SysV IPC objects are created. All state is local arguments and errno.

Dependencies: Requires `__NR_ipc` and Linux IPC headers; otherwise the file compiles to a skip test. s390 argument count formatting is handled specially.

Integration points: Validates the legacy ipc multiplexer decoder and its version-bit interpretation before per-family SysV IPC tests run.

Risks: The legacy syscall is architecture-specific and unavailable on many targets. Kernel behavior around version encoding determines which branch is printed.

Test signals: Expected output includes raw `ipc(...)` lines, decoded `semctl` EFAULT, optional `msgrcv`, and final exit.

Source read signal: complete file read for this research pass; file size 102 line(s), 2195 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.c -->
