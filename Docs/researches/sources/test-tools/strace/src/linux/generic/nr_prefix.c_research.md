# sources/test-tools/strace/src/linux/generic/nr_prefix.c

Purpose: supplies the syscall-number prefix string for `generic` personality-specific syscall rendering.

Important APIs/types/functions: nr_prefix.c; notable register references include none in this file.

Control flow: generic unknown-syscall formatting calls the prefix helper before printing raw syscall numbers.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on active personality selection and shared prefix helper contracts.

Risks/test signals: test unknown syscall rendering in native and compat personalities.

Source-read signal: reviewed complete local file (18 lines).
