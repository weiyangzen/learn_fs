# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_sp.c

## Summary
Stub service-provider functions for the fiber backend.

## Key Details
- `rumpuser_sp_init` returns success and `rumpuser_sp_fini` is a no-op.
- Signal raise, copyin/copyout, string copy, and anonymous mmap service-provider operations all call `abort()`.
- The file comment states these service-provider functions are not supported for fibers yet.

## Notes
This is an intentional unsupported surface rather than a partial implementation.
