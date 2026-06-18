# File Research: sources/os/bsd/freebsd-src/sys/sys/_tls_variant_i.h

Variant I thread-local storage layout.

Key elements:
- Defines `TLS_VARIANT_I`.
- Defines `struct dtv_slot`, `struct dtv`, and `struct tcb`.
- Defines `TLS_TCB_SIZE`.

Dependencies:
- Requires `uintptr_t` from included type context.
- Forward-declares `struct pthread`.

Research notes:
- TCB layout is shared across architectures using TLS variant I.
- `tcb_dtv` is required by the runtime linker.
