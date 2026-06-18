# sources/test-tools/strace/src/linux/alpha/arch_getrval2.c

Purpose: returns the architecture-specific second syscall return value for `alpha`.

Important APIs/types/functions: getrval2; notable register references include none in this file.

Control flow: fetches registers if needed, then returns the ABI register used for the secondary result.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on ptrace register fetch helpers and architecture return-register layout.

Risks/test signals: validate syscalls with paired return values, plus ptrace fetch failure paths.

Source-read signal: reviewed complete local file (15 lines).
