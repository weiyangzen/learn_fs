# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf.c

Generic unsigned `u_quad_t` to `double` conversion. It splits the integer into high and low words and computes `high * 2^32 + low`.

This is the unsigned analogue of `floatdidf.c`, without sign handling.
