# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_date.c

Read completely: 128 lines.

Implements `ns_datetosecs()`, converting DNS date strings in `yyyymmddhhmmss` format to seconds since 1970-01-01 UTC. It validates fixed length, numeric fields, year/month/day/hour/minute/second ranges, and then computes the timestamp manually instead of relying on `timegm()`.

Leap years are handled explicitly. The accepted year range begins at 1990 and extends to 9999, but the return type is `u_int32_t`, so distant future dates wrap modulo 32 bits. The helper `datepart()` leaves an accumulated error flag set if any field fails validation.
