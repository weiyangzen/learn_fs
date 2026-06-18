# sources/test-tools/strace/src/signalfd.c

Purpose: decodes `signalfd` and `signalfd4`.

Important APIs/types/functions: `do_signalfd`, `SYS_FUNC(signalfd)`, `SYS_FUNC(signalfd4)`, `print_sigset_addr_len`, `sfd_flags`, and return flag `RVAL_FD`.

Control flow: shared helper prints fd, mask pointer using the supplied size, size value, and optionally flags for the four-argument variant.

State and persistence behavior: stateless; reads the mask from tracee memory during entry decode.

Dependencies and integration points: relies on signal mask printer from `signal.c`, kernel fd flag constants, and syscall return formatting as a file descriptor.

Risks: kernel requires `sizemask == NSIG_BYTES`, but the decoder prints arbitrary sizes defensively. Flag argument index must remain `3` only for `signalfd4`.

Test signals: signalfd versus signalfd4, known/unknown `SFD_*` flags, invalid mask pointer, nonstandard size, and fd return annotation.
