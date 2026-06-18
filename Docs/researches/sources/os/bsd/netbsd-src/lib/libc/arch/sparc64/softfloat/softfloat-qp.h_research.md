# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-qp.h

## Summary
Renames SoftFloat symbols for SPARC64 quad-precision libc use.

## Key Details
- Under `SOFTFLOATSPARC64_FOR_GCC`, maps common SoftFloat global names to `_softfloat_*` names.
- Renames single, double, and quad operations to avoid exporting unintended user-visible names.
- Defines `SOFTFLOAT_FOR_GCC` after namespace renaming when needed.
- Ensures `FLOAT128` code can be compiled while keeping SoftFloat internals out of the normal libc namespace.

## Notes
This is primarily a namespace isolation header for building SPARC64 quad support.
