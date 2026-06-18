# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl.h

## Purpose
Shared declarations for `bectl` source files.

## Main Elements
- Declares `usage()`.
- Declares jail, unjail, and list command handlers.
- Exposes global `libbe_handle_t *be`.

## Dependencies And Integration
Included by `bectl.c`, `bectl_jail.c`, and `bectl_list.c`.

## Risk Notes
The global libbe handle keeps command modules simple but makes handlers depend on `main()` initialization order.
