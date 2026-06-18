# File Research: sources/os/bsd/netbsd-src/sys/sys/csan.h

Declares KCSAN kernel concurrency sanitizer initialization hooks.

Key content:
- Includes `opt_kcsan.h` when `_KERNEL_OPT` is defined.
- Includes `<sys/types.h>`.
- Under `KCSAN`: declares `kcsan_init` and `kcsan_cpu_init`.
- Without `KCSAN`: both macros compile to `__nothing`.

Important behavior:
- Provides zero-cost stubs when sanitizer support is disabled.
- `kcsan_cpu_init` takes `struct cpu_info *` without a local forward declaration, relying on surrounding kernel context.
