# sources/test-tools/strace/src/kernel_time_types.h

Purpose: provides fallback kernel time type definitions when system headers lack modern Linux time structs.

Important APIs/types/functions: `struct __kernel_sock_timeval`, `__kernel_timespec`, `kernel_timespec64_t`, and feature macros `HAVE_STRUCT___KERNEL_SOCK_TIMEVAL`/`HAVE_STRUCT___KERNEL_TIMESPEC`.

Control flow: includes `kernel_timespec.h`, then includes `<linux/time_types.h>` when it provides needed structs; otherwise includes `<stdint.h>`. Missing `__kernel_sock_timeval` is defined with 64-bit seconds/useconds, and missing `__kernel_timespec` is aliased to `kernel_timespec64_t`.

State and persistence behavior: no runtime state; compile-time compatibility only.

Dependencies and integration points: used by decoders and generated ioctl definitions needing modern kernel socket/time layouts independent of host header vintage.

Risks: fallback definitions must match Linux UAPI exactly. Incorrect feature detection could conflict with system headers or mis-size timeout structures.

Test signals: build on old and new kernel headers, compile users of socket timeval and timespec ioctls, and verify decoded 64-bit time fields.
