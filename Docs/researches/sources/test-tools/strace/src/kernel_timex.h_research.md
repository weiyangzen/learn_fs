# sources/test-tools/strace/src/kernel_timex.h

Purpose: defines kernel `timex` layouts for time adjustment syscalls across 64-bit, sparc64, and time32 ABIs.

Important APIs/types/functions: `kernel_timex64_t`, `kernel_sparc64_timex_t`, `kernel_timex32_t`, embedded `kernel_timeval64_t`, and `HAVE_ARCH_TIME32_SYSCALLS`.

Control flow: always defines the y2038-safe 64-bit layout, conditionally defines sparc64's special layout with `int tv_usec`, and conditionally defines the legacy time32 layout using 32-bit scalar fields.

State and persistence behavior: no state; structure definitions only.

Dependencies and integration points: includes `kernel_timeval.h`; used by `adjtimex`/`clock_adjtime` decoders and any tests validating `struct timex` tracee layouts.

Risks: padding fields and architecture-specific timeval layout preserve ABI size; removing or reordering them would break mpers-independent decoding.

Test signals: cover time64 and time32 `timex` decoding, nonzero padding arrays, TAI/status fields, and sparc64-specific structure if available.
