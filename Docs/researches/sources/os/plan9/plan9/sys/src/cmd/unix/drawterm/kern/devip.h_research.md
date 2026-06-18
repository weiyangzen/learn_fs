# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.h

Defines the OS socket abstraction used by `devip.c`.

Contents:
- Protocol identifiers `S_TCP` and `S_UDP`.
- Prototypes for socket create/connect/bind/listen/accept/send/recv/getsockname.
- Prototypes for service and host lookup helpers.
- `hostlookup` returns a string representation suitable for Plan 9 IP parsing.

Role:
- Keeps core Plan 9 network device logic independent of POSIX vs Winsock details.
