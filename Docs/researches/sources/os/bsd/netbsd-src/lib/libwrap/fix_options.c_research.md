# File Research: sources/os/bsd/netbsd-src/lib/libwrap/fix_options.c

## Purpose
Inspects and rejects dangerous IPv4 socket options, especially source routing.

## Key Details
- Compiled behavior is under `IP_OPTIONS`.
- Checks socket family with `getsockname`; only handles `AF_INET`.
- Gets IP options via `getsockopt`.
- Rejects `IPOPT_LSRR` and `IPOPT_SSRR` by logging and shutting down the fd.
- Rejects malformed option lengths.
- Logs non-routing IP options and attempts to clear them with `setsockopt`.

## Dependencies and Role
- Network hardening helper for TCP wrappers.
