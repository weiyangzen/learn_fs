# sources/user-network-fs/pyfuse3/src/pyfuse3/gettime.h

Purpose: Provides `gettime_realtime` as a platform-independent helper for real-time clock retrieval.

Important APIs/types/functions: Static function `gettime_realtime(struct timespec *tp)` maps to `clock_gettime(CLOCK_REALTIME, tp)` on Linux/BSD and to `gettimeofday` with microsecond-to-nanosecond conversion on Darwin.

Control flow: Preprocessor branches on `PLATFORM` from `pyfuse3.h`. Unknown platforms fail compilation.

State and persistence: No state; writes the current wall-clock time into the provided `timespec`.

Dependencies and integration points: Uses `<time.h>` on Linux/BSD and `<sys/time.h>` on Darwin. Native pyfuse3 code can use this instead of conditional clock code.

Risks: Darwin fallback has microsecond resolution, so nanosecond fields are not true nanosecond precision there. Wall-clock time can jump with system clock changes.

Test signals: Timestamp rounding tests and filesystem timestamp tests indirectly exercise the native timestamp plumbing that relies on time conversions.
