# File Research: sources/os/bsd/netbsd-src/lib/libwrap/clean_exit.c

## Purpose
Terminates a wrapped daemon cleanly after discarding pending datagram input when needed.

## Key Details
- Calls `request->sink(request->fd)` if a sink function is configured.
- Sleeps 5 seconds to avoid noisy inetd loops.
- Calls `exit(0)`.

## Dependencies and Role
- TCP wrappers control-flow helper for refusing/aborting service safely.
