# sources/test-tools/strace/src/linux/aarch64/arch_sigreturn.c

Purpose: reuses shared strace architecture logic for `aarch64` by including `../arm/arch_sigreturn.c` from `arch_sigreturn.c`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../arm/arch_sigreturn.c` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
