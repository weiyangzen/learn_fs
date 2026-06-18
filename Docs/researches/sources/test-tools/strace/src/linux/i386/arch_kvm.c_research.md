# sources/test-tools/strace/src/linux/i386/arch_kvm.c

Purpose: reuses shared strace architecture logic for `i386` by including `../x86_64/arch_kvm.c` from `arch_kvm.c`.

Important APIs/types/functions: this file exports the APIs provided by the included implementation rather than defining new local functions.

Control flow: the C preprocessor splices the target file into this architecture build, so runtime behavior is the shared implementation's behavior under this architecture's register/personality macros.

State/persistence behavior: no independent state; included code operates on the surrounding architecture register globals and `struct tcb` state.

Dependencies/integration: direct dependency on `../x86_64/arch_kvm.c` and the macro/register contract expected by that file.

Risks/test signals: changes in the shared implementation can silently affect this architecture; compile the architecture and run syscall/signal/ioctl traces that exercise the included path.

Source-read signal: reviewed complete local file (1 lines).
