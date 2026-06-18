# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parseipfexpr.c

Parser for IPFilter expression syntax into packed kernel expression arrays.

Key behavior:
- Supports operands such as `ip.addr`, `ip.src`, `ip.dst`, IPv6 variants, `ip.p`, TCP/UDP ports, TCP flags/state, and `idle-gt`.
- Removes all whitespace and requires semicolon-terminated expressions.
- Builds an integer array prefixed with total size and terminated with `IPF_EXP_END`.
- Encodes command metadata in `ipfexp_t` records followed by typed integer arguments.

Research notes:
- `arg < ops + 2` is evaluated before `arg == NULL`, making missing `=` handling fragile.
- Error strings may be static or allocated by `asprintf()`; ownership is not documented.
