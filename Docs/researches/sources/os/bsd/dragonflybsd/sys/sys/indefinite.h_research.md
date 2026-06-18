# File Research: sources/os/bsd/dragonflybsd/sys/sys/indefinite.h

`indefinite.h` defines state for tracking indefinite waits in contention loops. It includes `machine/clock.h`.

It declares `lock_test_mode` and `indefinite_uses_rdtsc`, defines `struct indefinite_info` with timing base, lock address, identifier, elapsed seconds, loop count, type, and reported flag, and typedefs it as `indefinite_info_t`.

`INDEF_INFO_START` controls how many loop iterations occur before timing begins. The inline operational logic is in `indefinite2.h`.
