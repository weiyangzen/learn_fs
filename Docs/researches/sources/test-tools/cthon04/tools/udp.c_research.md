# sources/test-tools/cthon04/tools/udp.c

## Purpose
is the UDP client for the simple Connectathon ping pair on port 3457.

## Important APIs, Types, and Functions
`main()` resolves hostname, creates a datagram socket, `sendto()`s a fixed message, `recvfrom()`s a reply, and validates the first byte changed.

## Control Flow and State
It sends one datagram to `UDP_PORT`, waits indefinitely for one response, compares length and payload, and prints success or a message error.

## Persistence and Dependencies
state is one UDP socket and server address. Dependencies: IPv4 UDP sockets, name resolution, and `udpd.c` server behavior.

## Integration Points, Risks, and Test Signals
Integration is a UDP connectivity diagnostic. Risks include no timeout/retry, spoofable reply source after `recvfrom`, obsolete hostent fields, and datagram loss. Signal is `udp ping to <host> ok`.
