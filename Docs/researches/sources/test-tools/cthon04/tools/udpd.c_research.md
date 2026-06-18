# sources/test-tools/cthon04/tools/udpd.c

## Purpose
is the UDP daemon for the simple Connectathon ping pair on port 3457.

## Important APIs, Types, and Functions
`main()` creates a UDP socket, binds `INADDR_ANY`, loops on `recvfrom()`, reverse-resolves the sender, increments the first byte of each datagram, and `sendto()`s it back.

## Control Flow and State
The daemon handles one datagram at a time forever and echoes the same byte count after mutating byte zero.

## Persistence and Dependencies
persistent state is the bound UDP socket; no files are touched. Dependencies: IPv4 UDP sockets, reverse DNS, and client `udp.c`.

## Integration Points, Risks, and Test Signals
Integration is with `udp.c`. Risks include no `SO_REUSEADDR`, no shutdown path, blocking reverse DNS, and unauthenticated echo behavior. Signals are request logs and successful client validation.
