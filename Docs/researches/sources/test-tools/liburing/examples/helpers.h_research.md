# sources/test-tools/liburing/examples/helpers.h

## sources/test-tools/liburing/examples/helpers.h

Purpose: Header exposing shared example helpers and compatibility declarations.

Important APIs/types: `T_ALIGN_UP(v, align)` macro; prototypes for `setup_listening_socket`, `t_aligned_alloc`, `t_error`, and `memfd_create`; conditional include of `<linux/memfd.h>` when config lacks memfd create.

Control flow: header-only declarations and macro expansion; no runtime flow.

State and persistence: none directly.

Dependencies/integration: included by examples that share socket setup, aligned allocation, and fatal error handling. Relies on generated `config-host.h` being force-included by build flags so `CONFIG_HAVE_MEMFD_CREATE` is meaningful.

Risks: `T_ALIGN_UP` assumes power-of-two alignment and can double-evaluate arguments. The unconditional `memfd_create` prototype under all configs must match libc signature.

Test signals: compile success across glibc, musl, Android-like configurations, and examples using these helpers.
