# sources/test-tools/strace/src/linux/aarch64/arch_get_personality.c

Purpose: maps ptrace syscall-info audit architecture values to the strace personality index for `aarch64`.

Important APIs/types/functions: get_personality_from_syscall_info; notable register references include none in this file.

Control flow: returns the compatibility personality when the syscall-info `arch` field matches the secondary audit architecture; otherwise the generic caller treats it as personality 0.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on `struct_ptrace_syscall_info` and Linux audit architecture constants.

Risks/test signals: wrong mapping dispatches to the wrong syscall table; test mixed native/compat traced processes.

Source-read signal: reviewed complete local file (13 lines).
