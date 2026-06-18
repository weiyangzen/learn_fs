# File Research: sources/os/bsd/freebsd-src/sbin/pflowctl/pflowctl.c

## Purpose
Command-line control utility for PFLOW exporters through FreeBSD generic netlink.

## Main Elements
- Parses operations: list (`-l`), create (`-c`), delete (`-d id`), set (`-s id ...`), and verbose (`-v`).
- Converts `pflowN` or numeric IDs to integer IDs.
- Uses snl parsers for list, create, get, and nested sockaddr attributes.
- `list()` enumerates PFLOW instances and calls `get()` for each.
- `create()` creates a pflow instance and prints its name.
- `del()` deletes an instance by ID.
- `get()` prints version, observation domain, source/destination addresses, and optional socket status.
- `set()` accepts `src`, `dst`, `proto`, and `domain`, parses numeric IPv4/IPv6 endpoint strings, and sends netlink SET attributes.

## Dependencies And Integration
Uses `<net/pflow.h>` generic netlink family constants and FreeBSD `snl` netlink helpers.

## Risk Notes
Address parsing is numeric-only and supports bracketed IPv6 port syntax. Operations fail if `pflow.ko` is not loaded.
