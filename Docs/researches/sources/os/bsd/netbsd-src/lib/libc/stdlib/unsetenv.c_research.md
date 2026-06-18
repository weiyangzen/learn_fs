# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/unsetenv.c

Implements `unsetenv(name)` using libc’s environment lock and owned-value helpers. It validates the name, finds the first matching slot, frees owned matching values, compacts nonmatching entries over all matching entries, clears stale tail slots to NULL, and unlocks.

Missing names are successful no-ops; invalid names set `EINVAL`.
