# sources/test-tools/strace/src/linux/generic/ptrace_pokeuser.c

Purpose: implements generic user-area register writes through `ptrace(PTRACE_POKEUSER)`.

Important APIs/types/functions: ptrace_pokeuser; notable register references include none in this file.

Control flow: writes a word to a user-area offset for syscall tampering helpers and propagates ptrace errors.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on ptrace, architecture user offsets, and register setter helpers.

Risks/test signals: wrong word size or offset corrupts tracee registers; test injected return values and syscall-number rewrites.

Source-read signal: reviewed complete local file (12 lines).
