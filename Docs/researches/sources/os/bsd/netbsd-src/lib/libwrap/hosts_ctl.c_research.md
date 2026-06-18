# File Research: sources/os/bsd/netbsd-src/lib/libwrap/hosts_ctl.c

## Purpose
Convenience wrapper around `hosts_access`.

## Key Details
- Initializes a `request_info` with daemon, client name, client address, and user.
- Calls `hosts_access`.
- Provides a simpler interface for common callers.

## Dependencies and Role
- Thin API wrapper for TCP wrappers.
