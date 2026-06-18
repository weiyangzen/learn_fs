# sources/test-tools/strace/src/sigevent.h

Purpose: local portable definition of a kernel-facing `sigevent`-like structure.

Important APIs/types/functions: `struct_sigevent` with `sigev_value`, `sigev_signo`, `sigev_notify`, `tid`, and thread callback/attribute union fields.

Control flow: header only; consumers fetch and print this layout.

State and persistence behavior: none.

Dependencies and integration points: used by timer/aio/mq style decoders that need a stable internal representation independent of libc header variation.

Risks: pointer width and union layout must match MPERS expectations in consuming files; new notification modes may require downstream print updates.

Test signals: timer or mq syscalls using `SIGEV_SIGNAL`, `SIGEV_THREAD_ID`, and thread callback forms across personalities.
