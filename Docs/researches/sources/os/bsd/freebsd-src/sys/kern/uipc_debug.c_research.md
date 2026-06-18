# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_debug.c

## Summary
Provides DDB-only debugger display commands for sockets, socket buffers, protocol switches, and protocol domains.

## Main Responsibilities
- Pretty-prints socket types, socket options, socket state bits, listen queue state, sockbuf state, sockbuf flags, protocol flags, domains, and protosw fields.
- Defines DDB `show socket`, `show sockbuf`, `show protosw`, and `show domain` commands.
- Recursively expands related structures, such as printing a socket's `so_proto` and that protocol's domain.

## Key APIs
- DDB commands: `db_show_socket`, `db_show_sockbuf`, `db_show_protosw`, `db_show_domain`.
- Internal printers: `db_print_socket()`, `db_print_sockbuf()`, `db_print_protosw()`, `db_print_domain()`.

## Important Behavior
All implementation is compiled only under `DDB`. The commands require an address argument and then treat it as the requested kernel structure pointer.

`db_print_socket()` distinguishes listen sockets from established/queued sockets. For listen sockets it prints incomplete/complete queue heads and queue lengths. For non-listen sockets it prints queue state, listener pointer, timeout/error fields, signal/oob state, and both receive and send sockbufs.

`db_print_sockbuf()` exposes mbuf chain pointers, accounting fields, low-water/timeouts, flags, and AIO queue head. The flag printers use a simple comma separator state and omit unknown bits.

## State and Synchronization
This is debugger inspection code and does not acquire socket, sockbuf, domain, or protocol locks. It is intended for DDB contexts where direct inspection is acceptable.

## Risks
The printers dereference live kernel pointers without validation beyond the user-provided address. Output can be stale or inconsistent if structures are changing, and invalid addresses can fault in debugger context.
