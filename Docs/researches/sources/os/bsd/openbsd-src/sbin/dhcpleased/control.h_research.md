# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.h

## Purpose
`control.h` declares the runtime control socket interface for non-`SMALL` builds.

## Exports
Under `#ifndef SMALL`, it declares:
- `control_init`
- `control_listen`
- `control_accept`
- `control_dispatch_imsg`
- `control_imsg_relay`

## Integration Notes
The header is included by main/frontend control paths and compiles to no declarations in `SMALL` builds.
