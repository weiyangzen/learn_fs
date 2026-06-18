# File Research: sources/os/bsd/openbsd-src/sys/sys/refcnt.h

Defines a small kernel reference counter abstraction with optional trace index.

Key contents:
- `struct refcnt` with volatile reference count and trace index.
- `REFCNT_INITIALIZER`.
- `refcnt_shared()` macro.
- DTrace/static tracing index constants for selected object types.

Kernel APIs:
- `refcnt_init`, `refcnt_init_trace`, `refcnt_take`, `refcnt_rele`, `refcnt_rele_wake`, `refcnt_finalize`, `refcnt_read`.

Risk notes:
- Used in shared lifetime control paths; callers must pair take/rele and use finalize only when ownership is complete.
