# File Research: sources/os/bsd/netbsd-src/sys/sys/tls.h

Read completely: 60 lines.

Defines machine TLS thread-control-block layout variants.

Key elements:
- Includes machine type definitions and supports either TLS variant I or variant II, but rejects both simultaneously.
- `struct tls_tcb` layout differs by variant:
  - Variant I stores dynamic thread vector and pthread pointer.
  - Variant II stores self pointer, dynamic thread vector, and pthread pointer.
- Public runtime loader declarations expose `_rtld_tls_allocate()` and `_rtld_tls_free()` when a TLS variant is supported.

Risks and notes:
- TCB layout is architecture ABI and runtime-linker sensitive.
- Incorrect variant selection breaks TLS and pthread private pointer access.
