# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/interror.c

IPFilter internal error-number translation table. It maps kernel/internal IPFilter error codes to stable text for filter, auth, frag, lookup, NAT, pool, proxy, scan, state, sync, destination-list, and FreeBSD ioctl/security failures.

Key behavior:
- `ipf_errors[]` is explicitly append-only; comments prohibit reusing gaps because numeric codes are external diagnostics.
- `find_error()` binary-searches the sorted table by `iee_number`.
- `ipf_geterror()` fetches the current internal error with `SIOCIPFINTERROR`; `ipf_strerror()` translates a supplied number.

Notable dependencies:
- `ipf.h`, `SIOCIPFINTERROR`, caller-supplied `ioctlfunc_t`.

Research notes:
- Correct ordering of `ipf_errors[]` is required for `find_error()` to work.
- Unknown or failed lookups return static fallback strings, so the API is not thread-safe.
