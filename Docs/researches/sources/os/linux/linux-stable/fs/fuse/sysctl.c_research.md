# File Research: sources/os/linux/linux-stable/fs/fuse/sysctl.c

## Purpose
Registers `/proc/sys/fs/fuse` tunables controlling FUSE request/page limits and request timeout defaults.

## Key Interfaces
- `fuse_sysctl_register()` registers the sysctl table.
- `fuse_sysctl_unregister()` unregisters it.
- Exposed tunables: `max_pages_limit`, `default_request_timeout`, and `max_request_timeout`.

## Design Notes
`max_pages_limit` is bounded by the u16 `fuse_init_out.max_pages` protocol field. Timeout values are also capped at `65535`, matching u16 request timeout fields.

## Dependencies
Uses Linux sysctl table registration and global FUSE tunable variables declared elsewhere.

## Risks And Invariants
The table header is stored globally and cleared on unregister. Bounds prevent users from configuring values the protocol cannot represent.
