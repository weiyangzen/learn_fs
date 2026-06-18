# sources/test-tools/cthon04/tools/tcp.c

## Purpose
is the TCP client for the simple Connectathon ping pair on port 3456.

## Important APIs, Types, and Functions
`main()` resolves a hostname with `gethostbyname()`, opens a TCP socket, connects, writes a fixed message, reads the echo, and validates the first byte was incremented by the daemon.

## Control Flow and State
The client requires one hostname, connects to `TCP_PORT`, writes `This is a test message!`, reads up to `BUFSIZ`, compares length and payload, and prints success or message error.

## Persistence and Dependencies
state is a single socket connection and local buffer. Dependencies: IPv4 sockets, DNS/hosts lookup, `tcpd.c` server behavior.

## Integration Points, Risks, and Test Signals
Integration is the basic TCP connectivity diagnostic. Risks include no timeout, obsolete `h_addr`, no explicit socket close, and partial write/read assumptions. Signals are `tcp ping to <host> ok`.
