# sources/test-tools/strace/src/kernel_timespec.h

Purpose: defines 64-bit and conditional 32-bit kernel timespec layouts.

Important APIs/types/functions: `kernel_timespec64_t`, `kernel_timespec32_t`, `HAVE_ARCH_TIME32_SYSCALLS`, `HAVE_ARCH_TIMESPEC32`, and `arch_defs.h`.

Control flow: always defines `kernel_timespec64_t` with `long long` seconds/nanoseconds. Defines `kernel_timespec32_t` only when the target architecture has time32 syscalls or timespec32 structures.

State and persistence behavior: no state; types are used for tracee-memory decoding.

Dependencies and integration points: included by time, timeout, futex, socket, and ioctl decoders that must distinguish y2038-safe and legacy layouts.

Risks: conditional availability must match syscall tables; decoding a 32-bit time syscall with the 64-bit type would misread both fields.

Test signals: cover time32 and time64 syscall variants, architectures without time32 support, negative seconds, and nanosecond boundary values.
