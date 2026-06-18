# File Research: sources/os/bsd/freebsd-src/sys/sys/_exterr.h

Kernel-side extended error record definition.

Key elements:
- Defines `struct kexterr` with numeric error, message pointer, two 64-bit parameters, category, and source line.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Added for richer kernel error reporting.
- Paired conceptually with `_uexterror.h`, which provides the fixed-size user ABI representation.
