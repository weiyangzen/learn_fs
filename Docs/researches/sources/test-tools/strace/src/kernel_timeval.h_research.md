# sources/test-tools/strace/src/kernel_timeval.h

Purpose: defines kernel timeval layouts used by old and 64-bit time APIs.

Important APIs/types/functions: `kernel_timeval64_t`, `kernel_old_timeval_t`, `kernel_long_t`, and sparc64-specific `tv_usec` sizing.

Control flow: header-only definitions; 64-bit timeval uses two `long long` fields, while old timeval uses `kernel_long_t` seconds and either `kernel_long_t` or sparc64 `int` microseconds.

State and persistence behavior: no state.

Dependencies and integration points: includes `kernel_types.h`; consumed by rusage, timex, v4l2, select/time, and other decoders needing kernel timeval ABI layouts.

Risks: sparc64 old timeval is a special case and can be misdecoded if treated as two kernel longs. Host libc `struct timeval` is not interchangeable with these types.

Test signals: timeval-decoding tests should cover native/compat personalities, sparc64 layout where available, and both old and 64-bit timeval users.
